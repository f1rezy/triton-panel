import tritonclient.http as httpclient

from flask import Blueprint
from flask import jsonify
from flask_jwt_extended import jwt_required

from database import db
from models import *

bp = Blueprint("triton", __name__)


@bp.route("/models", methods=["GET"])
@jwt_required()
def get_triton_loaded_models():
    return jsonify([
        {
            "model_id": version.model_version.model_id,
            "model_name": version.model_version.model.name,
            "version_id": version.model_version_id,
            "version_name": version.model_version.name,
            "triton_loaded_version_id": version.id,
        } for version in db.session.query(TritonLoaded).all()])


@bp.route("/model_version/<id>", methods=["POST"])
@jwt_required()
def add_model_to_triton(id: str):
    version = db.session.query(Version).filter(Version.id == id).first()
    if not version:
        return jsonify({"status": False}), 404

    triton_client = httpclient.InferenceServerClient(url="localhost:8000", verbose=False)
    model_name = "simple"

    triton_client.load_model(model_name)
    if not triton_client.is_model_ready(model_name):
        return jsonify({"status": False})

    # config = open(f"models_onnx/{model_name}/{version.name}/config.pbtxt", mode="r").read()
    config = "{\"max_batch_size\":\"16\"}"
    triton_client.load_model(model_name, config=config)
    if triton_client.is_model_ready(model_name):
        return jsonify({"dadadada": True})

    # triton_loaded = TritonLoaded(model_version_id=version.id)
    # db.session.add(triton_loaded)
    # db.session.commit()
    triton_client.unload_model(model_name)

    return jsonify({"status": True}), 200


@bp.route("/model_version/<id>", methods=["DELETE"])
@jwt_required()
def delete_model_from_triton(id: str):
    version = db.session.query(Version).filter(Version.id == id).first()
    model = db.session.query(Model).filter(Model.id == version.model_id).first()
    if not model:
        return jsonify({"status": False}), 404

    triton_loaded = db.session.query(TritonLoaded).filter(TritonLoaded.model_version_id == version.id).first()
    if not triton_loaded:
        return jsonify({"status": False}), 404

    triton_client = httpclient.InferenceServerClient(url="localhost:8000",
                                                     verbose=False)
    model_name = model.name
    triton_client.unload_model(model_name)

    db.session.delete(triton_loaded)
    db.session.commit()

    return jsonify({"status": True}), 200

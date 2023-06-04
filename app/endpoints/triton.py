import shutil
import tritonclient.grpc as grpcclient

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

    if [version.triton_loaded_version for version in version.model.versions]:
        return jsonify({"status": False})

    source_path = "models_onnx/" + version.model.name + "/" + version.name
    destination_path = "model_repository/" + version.model.name
    shutil.copytree(source_path, destination_path)

    triton_client = grpcclient.InferenceServerClient(url="triton:8001", verbose=False)
    model_name = version.model.name

    triton_client.load_model(model_name)
    if not triton_client.is_model_ready(model_name):
        return jsonify({"status": False})

    triton_loaded = TritonLoaded(model_version_id=version.id)
    db.session.add(triton_loaded)
    db.session.commit()

    return jsonify({"status": True}), 200


@bp.route("/model_version/<id>", methods=["DELETE"])
@jwt_required()
def delete_model_from_triton(id: str):
    version = db.session.query(Version).filter(Version.id == id).first()
    if not version:
        return jsonify({"status": False}), 404

    triton_loaded = db.session.query(TritonLoaded).filter(TritonLoaded.model_version_id == version.id).first()
    if not triton_loaded:
        return jsonify({"status": False}), 404

    triton_client = grpcclient.InferenceServerClient(url="triton:8001", verbose=False)
    model_name = version.model.name
    triton_client.unload_model(model_name)
    if triton_client.is_model_ready(model_name):
        return jsonify({"status": False})

    path = "model_repository/" + version.model.name
    shutil.rmtree(path)

    db.session.delete(triton_loaded)
    db.session.commit()

    return jsonify({"status": True}), 200

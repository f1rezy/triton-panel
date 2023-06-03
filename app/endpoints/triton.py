import os
import shutil

from flask import Blueprint
from flask import jsonify, request
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
        jsonify({"status": False}), 404

    source_path = os.path.abspath("models_onnx") + "/" + version.model.name + "/" + version.name
    destination_path = "/home/model_repository/" + version.model.name
    shutil.copytree(source_path, destination_path)

    triton_loaded = TritonLoaded(model_version_id=version.id)
    db.session.add(triton_loaded)
    db.session.commit()

    return jsonify({"status": True, "path": source_path}), 200


@bp.route("/model/<id>", methods=["DELETE"])
@jwt_required()
def delete_model_from_triton(id: str):
    model = db.session.query(Model).filter(Model.id == id).first()
    if not model:
        return jsonify({"status": False}), 404

    triton_loaded = list(filter(lambda x: x.triton_loaded_version, model.versions))
    if not bool(triton_loaded):
        return jsonify({"status": False}), 404

    path = os.path.abspath("model_repository") + "/" + model.name
    shutil.rmtree(path)

    triton_loaded = triton_loaded[0]
    db.session.delete(triton_loaded)
    db.session.commit()

    return jsonify({"status": True}), 200

from flask import Blueprint
from flask import jsonify, request
from flask_jwt_extended import jwt_required
import tritonclient.http as tc

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
            "triton_loaded_version_id": version.id
        } for version in db.session.query(TritonLoaded).all()])


@bp.route("/model_version/<id>", methods=["POST"])
@jwt_required()
def add_model_to_triton(id: str):
    return jsonify({"status": True})


@bp.route("/triton_loaded_version/<id>", methods=["DELETE"])
@jwt_required()
def delete_model_from_triton(id: str):
    return jsonify({"status": True})

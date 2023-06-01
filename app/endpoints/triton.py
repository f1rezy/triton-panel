from flask import Blueprint
from flask import jsonify, request
from flask_jwt_extended import jwt_required

from database import db
from db_models import *

bp = Blueprint("triton", __name__)


@bp.route("/models", methods=["GET"])
@jwt_required()
def get_triton_loaded_models():
    return jsonify([{model.data} for model in db.session.query(Model).all()])


@bp.route("/model/<id>", methods=["POST"])
@jwt_required()
def add_model_to_triton(id: int):
    return jsonify({"status": True})


@bp.route("/model/<id>", methods=["DELETE"])
@jwt_required()
def delete_model_from_triton(id: int):
    return jsonify({"status": True})

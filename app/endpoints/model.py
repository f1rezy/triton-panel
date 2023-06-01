from flask import Blueprint
from flask import jsonify, request
from flask_jwt_extended import JWTManager, jwt_required

from database import db
from db_models import *

bp = Blueprint('api', __name__)


@bp.route("/<id>", methods=["POST"])
@jwt_required()
def post_model(id: int):
    return jsonify({"status": True})


@bp.route("/<id>", methods=["DELETE"])
@jwt_required()
def delete_model(id: int):
    return jsonify({"status": True})

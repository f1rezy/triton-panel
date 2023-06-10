from flask import Blueprint
from flask import jsonify
from flask_jwt_extended import jwt_required

from database import db
from models import *

bp = Blueprint("models", __name__)


@bp.route("", methods=["GET"])
@jwt_required()
def get_models():
    return jsonify([
        {
            "id": model.id,
            "name": model.name,
            "triton_loaded": bool(list(filter(lambda x: x.triton_loaded_version, model.versions)))
        } for model in db.session.query(Model).all()])

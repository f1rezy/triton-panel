from flask import Blueprint
from flask import jsonify
from flask_jwt_extended import jwt_required

from database import db
from models import *

bp = Blueprint("models", __name__)


@bp.route("", methods=["GET"])
@jwt_required()
def get_models():
    return jsonify([model.data for model in db.session.query(Model).all()])

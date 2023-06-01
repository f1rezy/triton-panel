from flask import Blueprint
from flask import jsonify
from flask_jwt_extended import JWTManager, jwt_required

from database import db
from db_models import *

bp = Blueprint('api', __name__)


@bp.route("", methods=["GET"])
@jwt_required()
def get_models():
    return jsonify([{model.data} for model in db.session.query(Model).all()])

from flask import Blueprint
from flask import jsonify, request
from flask_jwt_extended import jwt_required

from database import db
from db_models import *

bp = Blueprint("model", __name__)


@bp.route("", methods=["POST"])
@jwt_required()
def post_model():
    name = request.form.get("name", None)

    model = db.session.query(Model).filter(Model.name == name).first()

    if not model and name:
        return jsonify({"status": True})

    return jsonify({"status": False})


@bp.route("/<id>", methods=["DELETE"])
@jwt_required()
def delete_model(id: int):
    model = db.session.query(Model).filter(Model.id == id).first()

    if model:
        db.session.delete(model)
        return jsonify({"status": True})

    return jsonify({"status": False})

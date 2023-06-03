import os
import shutil

from flask import Blueprint, send_file, after_this_request
from flask import jsonify, request
from flask_jwt_extended import jwt_required

from database import db
from models import *

bp = Blueprint("model", __name__)


@bp.route("/<id>", methods=["GET"])
@jwt_required()
def get_model(id: str):
    model = db.session.query(Model).filter(Model.id == id).first()

    if not model:
        return jsonify({"status": False}), 404

    return jsonify(
        {
            "id": model.id,
            "name": model.name,
            "versions": [
                {"id": version.id, "name": version.name,
                 "triton_loaded": True if version.triton_loaded_version else False}
                for version in model.versions
            ]
        })


@bp.route("/version", methods=["GET"])
@jwt_required()
def get_version():
    model_id = request.json.get("model_id", None)
    version_name = request.json.get("version_name", None)

    model = db.session.query(Model).filter(Model.id == model_id).first()
    version = db.session.query(Version).filter(Version.name == version_name, Version.model == model).first()

    if not model or not version:
        return jsonify({"status": False}), 404

    directory = os.path.abspath("models_onnx") + "/" + model.name + "/" + version_name
    filename = f"{model.name}-{version.name}"
    file = shutil.make_archive(filename, 'zip', root_dir=directory)
    filename += ".zip"

    @after_this_request
    def remove_file(response):
        try:
            os.remove(filename)
        except Exception as error:
            print(error)
        return response

    return send_file(file, download_name=filename, as_attachment=True)


@bp.route("", methods=["POST"])
@jwt_required()
def post_model():
    uploaded_files = request.files.getlist("file[]")

    if uploaded_files:
        name = uploaded_files[0].filename.split("/")[0]
        model = db.session.query(Model).filter(Model.name == name).first()
        if not model:
            model = Model(name=name)
            db.session.add(model)
            db.session.commit()
            model = db.session.query(Model).filter(Model.name == name).first()
            model.versions.append(Version(name="v1", model_id=model.id))
            db.session.commit()
            for file in uploaded_files:
                path = os.path.abspath("models_onnx") + "/" + name + "/v1/" + "/".join(file.filename.split("/")[1:])
                dir_path = "/".join(path.split("/")[:-1])
                if not os.path.isdir(dir_path):
                    os.makedirs(dir_path)
                file.save(path)
            return jsonify({"status": True}), 200

        return jsonify({"status": True, "id": model.id}), 208

    return jsonify({"status": False}), 204


@bp.route("/<id>", methods=["PUT"])
@jwt_required()
def put_model(id: str):
    uploaded_files = request.files.getlist("file[]")
    model = db.session.query(Model).filter(Model.id == id).first()

    if not model:
        return jsonify({"status": False}), 404

    if uploaded_files:
        version = f"v{int(model.versions[-1].name[1]) + 1}"
        model.versions.append(Version(name=version, model_id=model.id))
        db.session.commit()
        for file in uploaded_files:
            path = os.path.abspath("models_onnx") + "/" + model.name + "/" + version + "/" + \
                   "/".join(file.filename.split("/")[1:])
            dir_path = "/".join(path.split("/")[:-1])
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)
            file.save(path)
        return jsonify({"status": True}), 200

    return jsonify({"status": False}), 208


@bp.route("/<id>", methods=["DELETE"])
@jwt_required()
def delete_model(id: str):
    model = db.session.query(Model).filter(Model.id == id).first()

    if model:
        for version in model.versions:
            if version.triton_loaded_version:
                db.session.delete(version.triton_loaded_version)
            db.session.delete(version)
        db.session.delete(model)
        db.session.commit()
        path = os.path.abspath("models_onnx")
        shutil.rmtree(path + "/" + model.name)
        return jsonify({"status": True}), 200

    return jsonify({"status": False}), 404


@bp.route("/version/<version_id>", methods=["DELETE"])
@jwt_required()
def delete_version(version_id: str):
    version = db.session.query(Version).filter(Version.id == version_id, ).first()

    if not version:
        return jsonify({"status": False}), 404

    if version.triton_loaded_version:
        db.session.delete(version.triton_loaded_version)
    db.session.delete(version)
    db.session.commit()
    path = os.path.abspath(version.model.name)
    shutil.rmtree(path + "/" + version.name)
    return jsonify({"status": True}), 200

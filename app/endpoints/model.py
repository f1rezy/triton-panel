import os
import shutil
import tritonclient.grpc as grpcclient

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
        return jsonify({"status": False}), 205

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


@bp.route("/version/<id>", methods=["GET"])
@jwt_required()
def get_version(id: str):
    version = db.session.query(Version).filter(Version.id == id).first()

    if not version:
        return jsonify({"status": False}), 404

    directory = os.path.abspath("models_onnx") + "/" + version.model.name + "/" + version.name
    filename = f"{version.model.name}-{version.name}"
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
    if not model:
        return jsonify({"status": False}), 404

    triton_loaded = db.session.query(TritonLoaded).filter(TritonLoaded.model_version_id.in_([i.id for i in model.versions])).all()
    if triton_loaded:
        path = os.path.abspath("model_repository") + "/" + model.name
        shutil.rmtree(path)

        for i in triton_loaded:
            db.session.delete(i)

    for version in model.versions:
        if version.triton_loaded_version:
            triton_client = grpcclient.InferenceServerClient(url="localhost:8000", verbose=False)
            model_name = version.model.name
            triton_client.unload_model(model_name)

            path = "model_repository/" + version.model.name
            shutil.rmtree(path)
            db.session.delete(version.triton_loaded_version)
        db.session.delete(version)
    db.session.delete(model)
    path = os.path.abspath("models_onnx")
    shutil.rmtree(path + "/" + model.name)
    db.session.commit()
    return jsonify({"status": True}), 200


@bp.route("/version/<version_id>", methods=["DELETE"])
@jwt_required()
def delete_version(version_id: str):
    version = db.session.query(Version).filter(Version.id == version_id, ).first()
    model = db.session.query(Model).filter(Model.id == version.model.id).first()

    if not version:
        return jsonify({"status": False}), 404

    if version.triton_loaded_version:
        db.session.delete(version.triton_loaded_version)
    db.session.delete(version)  
    path = os.path.abspath("models_onnx")
    shutil.rmtree(path + "/" + version.model.name + "/" + version.name)
    if not model.versions:
        delete_model(model.id)
        db.session.commit()
        return jsonify({"status": True, "model_delete": True}), 200

    db.session.commit()
    return jsonify({"status": True, "model_delete": False}), 200

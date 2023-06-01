import datetime
import json
import os
from random import choices
from uuid import uuid4

from flask import Blueprint
from flask import jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies, unset_jwt_cookies, jwt_required, \
    current_user, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from uuid import UUID

from database import db
from models import User, Task

UPLOAD_FOLDER = os.path.abspath('files')
ALLOWED_EXTENSIONS = {'mp4', 'pdf', 'png', 'jpg', 'jpeg'}

bp = Blueprint('api', __name__)

jwt = JWTManager()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


@bp.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.datetime.now(datetime.timezone.utc)
        target_timestamp = datetime.datetime.timestamp(now + datetime.timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            print("new token")
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response


@bp.route("/students", methods=["GET"])
@jwt_required()
def get_students():
    if current_user.isAdmin is True:
        users = User.query.filter_by(isAdmin=False).all()
        return jsonify({'users': [user.data for user in users]})
    else:
        return jsonify({"status": False, "message": "У мужлан нет прав"}), 401


@bp.route("/is_admin", methods=["GET"])
@jwt_required()
def is_admin():
    if current_user.isAdmin:
        return jsonify({"status": True})
    else:
        return jsonify({"status": False})
    return jsonify({"status": False, "message": "У мужлан нет прав"}), 401


@bp.route("/update_code", methods=["GET"])
@jwt_required()
def update_code():
    if current_user.isAdmin:
        while True:
            code = "".join(choices("1234567890", k=6))
            codes = [i.code for i in User.query.filter_by(isAdmin=True).all()]
            if code in codes:
                continue
            break
        current_user.code = code
        db.session.commit()
        return jsonify({"status": True, "code": code})
    else:
        return jsonify({"status": False, "message": "У мужлан нет прав"}), 401


@bp.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    tasks_data = json.loads(current_user.tasks)
    print(tasks_data.keys())
    tasks = db.session.query(Task).all()
    return jsonify([task.data | {"status": tasks_data[str(task.id)]} for task in tasks if str(task.id) in tasks_data.keys()])


@bp.route("/task/", methods=["GET"])
@jwt_required()
def get_task():
    task_id = UUID(request.args.get("task_id", None))
    task = Task.query.filter_by(id=task_id).one_or_none()
    return jsonify(task.data)


@bp.route("/task", methods=["POST"])
@jwt_required()
def post_task():
    if current_user.isAdmin:
        title = request.json.get("title", None)
        description = request.json.get("description", None)
        type = request.json.get("type", None)
        people_id = request.json.get("people_id", None)
        task = Task.query.filter_by(title=title).one_or_none()
        if not task and title and people_id and type:
            task = Task(title=title, description=description, type=type, fp="DICK", people_id=people_id)
            db.session.add(task)
            users = db.session.query(User).all()
            for user in users:
                if str(user.id) in people_id:
                    user.tasks = json.dumps(json.loads(user.tasks) | {str(task.id): False})
                    db.session.commit()

            db.session.commit()
            return jsonify({"status": True})
        return jsonify({"status": False})


@bp.route("/set_task_status", methods=["PUT"])
@jwt_required()
def set_task_status():
    task_id = request.json.get("task_id", None)
    data = json.loads(current_user.tasks)
    data[str(task_id)] = True
    current_user.tasks = json.dumps(data)
    db.session.commit()
    return jsonify({"status": True})


@bp.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    print(request.json)
    print(username, password)
    try:
        user = User.query.filter_by(username=username).one_or_none()
    except Exception as e:
        return jsonify({"msg": "error"})

    if not user or not user.check_password(password):
        return jsonify({"status": False}), 401

    response = jsonify({"status": True})
    access_token = create_access_token(identity=user.id)
    set_access_cookies(response, access_token)
    return response


@bp.route("/register", methods=["POST"])
def register():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(username=username).one_or_none()

    if not user and username and password:
        db.session.add(User(username=username, password_hash=generate_password_hash(password)))
        db.session.commit()
        return jsonify({"status": True})

    return jsonify({"status": False})


@bp.route("/logout", methods=["POST"])
def logout_with_cookies():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@bp.route("/get_user_data", methods=["GET"])
@jwt_required()
def get_user_data():
    return jsonify(current_user.data)
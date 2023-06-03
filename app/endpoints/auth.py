import os
import datetime

from flask import Blueprint
from flask import jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies, unset_jwt_cookies, \
    get_jwt_identity, get_jwt

bp = Blueprint("auth", __name__)

jwt = JWTManager()


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


@bp.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username == os.environ.get("USERNAME", "admin") or not password == os.environ.get("PASSWORD", "admin"):
        return jsonify({"status": False}), 401

    response = jsonify({"status": True})
    access_token = create_access_token(identity="admin")
    set_access_cookies(response, access_token)
    return response


@bp.route("/logout", methods=["POST"])
def logout_with_cookies():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

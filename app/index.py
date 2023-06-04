import os
from datetime import timedelta

from flask import Flask
from flask_migrate import Migrate
from endpoints import *
from endpoints.auth import jwt
from database import db
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL",
                                                  r"postgresql://admin:password@37.139.40.124:5432/base")
app.config['UPLOAD_FOLDER'] = os.path.abspath("models_onnx")
app.config["JSON_AS_ASCII"] = False
app.config["JSON_SORT_KEYS"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config["JWT_SECRET_KEY"] = "secret"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
# app.config["JWT_COOKIE_SAMESITE"] = "NONE"
# app.config["JWT_COOKIE_SECURE"] = True

cors = CORS(app, resources={r"/api/*": {"origins": "*", "supports_credentials": True}})
db.init_app(app)
migrate = Migrate(app, db)
jwt.init_app(app)

app.register_blueprint(auth_router, url_prefix="/api/user")
app.register_blueprint(models_router, url_prefix="/api/models")
app.register_blueprint(model_router, url_prefix="/api/model")
app.register_blueprint(triton_router, url_prefix="/api/triton")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()

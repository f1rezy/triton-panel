from database import db
from .base import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import VARCHAR


class User(BaseModel):
    __tablename__ = "users"
    username = db.Column(VARCHAR(80), unique=True)
    password_hash = db.Column(db.String(128))

    @property
    def data(self):
        return {
            "id": self.id,
            "username": self.username
        }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

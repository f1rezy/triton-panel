from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.dialects.postgresql import SMALLINT

from database import db
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    username = db.Column(db.VARCHAR(80), unique=True)
    name = db.Column(db.VARCHAR(80))
    surname = db.Column(db.VARCHAR(80))
    height = db.Column(SMALLINT())
    weight = db.Column(SMALLINT())
    password_hash = db.Column(db.String(128))
    isAdmin = db.Column(db.BOOLEAN())
    code = db.Column(db.VARCHAR(6))
    tasks = db.Column(db.TEXT(), default="{}")

    @property
    def data(self):
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "surname": self.surname,
            "height": self.height,
            "weight": self.weight,
            "isAdmin": self.name,
        }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
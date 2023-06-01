import json

from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.dialects.postgresql import ARRAY, UUID

from database import db
from .base import BaseModel


class Task(BaseModel):
    __tablename__ = "tasks"

    title = db.Column(db.VARCHAR(80))
    description = db.Column(db.TEXT())
    type = db.Column(db.VARCHAR(80))
    fp = db.Column(db.VARCHAR(80))
    people_id = db.Column(ARRAY(item_type=UUID))

    @property
    def data(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.type,
            "fp": self.fp,
            "people_id": self.people_id,
        }
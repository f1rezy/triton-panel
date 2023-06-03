from database import db
from .base import BaseModel
from sqlalchemy.dialects.postgresql import VARCHAR


class Model(BaseModel):
    __tablename__ = "model"

    name = db.Column(VARCHAR(80))

    versions = db.relationship("Version", back_populates="model")

    @property
    def data(self):
        return {
            "id": self.id,
            "name": self.name
        }

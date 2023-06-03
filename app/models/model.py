from database import db
from .base import BaseModel
from sqlalchemy.dialects.postgresql import VARCHAR


class Model(BaseModel):
    __tablename__ = "model"

    name = db.Column(VARCHAR(80))

    versions = db.relationship("Version", back_populates="model")

    @property
    def data(self):
        triton_loaded = bool(list(filter(lambda x: x.triton_loaded_version, self.versions)))
        return {
            "id": self.id,
            "name": self.name,
            "triton_loaded": triton_loaded
        }

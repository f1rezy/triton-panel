from database import db
from .base import BaseModel
from sqlalchemy.dialects.postgresql import VARCHAR


class Version(BaseModel):
    __tablename__ = "version"

    name = db.Column(VARCHAR(80))
    model_id = db.Column(db.ForeignKey("model.id"))

    model = db.relationship("Model", back_populates="versions")
    triton_loaded_version = db.relationship("TritonLoaded", back_populates="model_version")

    @property
    def data(self):
        return {
            "id": self.id,
            "name": self.name,
            "model_id": self.model_id
        }

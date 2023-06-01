from database import db
from .base import BaseModel
from sqlalchemy.dialects.postgresql import VARCHAR


class TritonLoaded(BaseModel):
    __tablename__ = "triton_loaded"

    model_version_id = db.Column(db.ForeignKey("version.id"))

    model_version = db.relationship("Version", back_populates="triton_loaded_version")

    @property
    def data(self):
        return {
            "id": self.id,
            "model_version_id": self.model_version_id
        }

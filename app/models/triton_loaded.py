from database import db
from .base import BaseModel


class TritonLoaded(BaseModel):
    __tablename__ = "triton_loaded"

    model_version_id = db.Column(db.ForeignKey("version.id"))

    model_version = db.relationship("Version", back_populates="triton_loaded_version")

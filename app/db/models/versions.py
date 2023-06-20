from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import VARCHAR, TIMESTAMP
from sqlalchemy.orm import relationship
import datetime

from app.db.models.base_class import Base


class Version(Base):
    __tablename__ = "versions"

    name = Column("name", VARCHAR(80), nullable=False)
    model_id = Column("model_id", ForeignKey("models.id"), nullable=False)
    upload_date = Column("upload_date", TIMESTAMP(timezone=True), default=datetime.datetime.now(), nullable=False)

    model = relationship("Model", back_populates="versions", lazy='selectin')
    triton_loaded_version = relationship("TritonLoaded", back_populates="version", lazy='selectin')

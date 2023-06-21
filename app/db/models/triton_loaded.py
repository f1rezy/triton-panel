from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.models.base_class import Base


class TritonLoaded(Base):
    __tablename__ = "triton_loaded"

    version_id = Column("model_version_id", ForeignKey("versions.id"), nullable=False)

    version = relationship("Version", back_populates="triton_loaded_version", lazy='selectin')

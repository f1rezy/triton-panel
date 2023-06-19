from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import VARCHAR
from sqlalchemy.orm import relationship

from app.db.models.base_class import Base


class Model(Base):
    __tablename__ = "models"

    name = Column("name", VARCHAR(80), nullable=False)

    versions = relationship("Version", back_populates="model")

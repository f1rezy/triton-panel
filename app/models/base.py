import uuid
from sqlalchemy.dialects.postgresql import UUID

from database import db


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)

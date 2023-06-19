from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db import DeclarativeBase


class Base(DeclarativeBase):
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    
    def __repr__(self):
        columns = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return f'<{self.__tablename__}: {", ".join(map(lambda x: f"{x[0]}={x[1]}", columns.items()))}>'

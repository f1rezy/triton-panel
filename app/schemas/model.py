from typing import Optional, List

from fastapi import UploadFile, File
from app.schemas.version import Version

from pydantic import BaseModel, UUID4


# Shared properties
class ModelBase(BaseModel):
    name: Optional[str] = None


# Properties to receive on model upload
class ModelUpload(ModelBase):
    pass
    
    
# Properties to receive on item update
class ModelUpdate(ModelBase):
    pass


# Properties shared by models stored in DB
class ModelInDBBase(ModelBase):
    id: UUID4
    name: str
    versions: List[Version] | None = None

    class Config:
        orm_mode = True


# Properties to return to client
class Model(ModelInDBBase):
    pass


# Properties properties stored in DB
class ModelInDB(ModelInDBBase):
    pass
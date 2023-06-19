from typing import Optional, List

from fastapi import UploadFile, File
from app.schemas.version import Version

from pydantic import BaseModel, UUID4


# Shared properties
class TritonLoadedBase(BaseModel):
    model_version_id: Optional[UUID4] = None


# Properties to receive on model upload
class TritonLoadedUpload(TritonLoadedBase):
    pass
    
    
# Properties to receive on item update
class TritonLoadedUpdate(TritonLoadedBase):
    pass


# Properties shared by models stored in DB
class TritonLoadedInDBBase(TritonLoadedBase):
    id: UUID4
    model_version_id: UUID4

    class Config:
        orm_mode = True


# Properties to return to client
class TritonLoaded(TritonLoadedInDBBase):
    pass


# Properties properties stored in DB
class TritonLoadedInDB(TritonLoadedInDBBase):
    pass

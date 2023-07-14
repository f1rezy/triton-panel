from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator, UUID4

from app.core.config import settings


# Shared properties
class VersionBase(BaseModel):
    name: Optional[str] = None
    model_id: Optional[UUID4] = None


# Properties to receive on version upload
class VersionUpload(VersionBase):
    name: str
    model_id: UUID4


# Properties to receive on version update
class VersionUpdate(VersionBase):
    pass


# Properties shared by models stored in DB
class VersionInDBBase(VersionBase):
    id: UUID4
    name: str
    model_id: UUID4
    upload_date: datetime
    triton_loaded: bool = False
    
    
    @validator("upload_date")
    def date_conversion(cls, value: datetime):
        return value.strftime(settings.DATE_TIME_FORMAT)
    

    class Config:
        from_attributes = True


# Properties to return to client
class Version(VersionInDBBase):
    pass


# Properties to return to client
class VersionConfig(VersionInDBBase):
    config: str


# Properties properties stored in DB
class VersionInDB(VersionInDBBase):
    pass

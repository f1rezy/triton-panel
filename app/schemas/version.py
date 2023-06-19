from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator, UUID4


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
    
    
    @validator("upload_date")
    def remove_timezone(cls, value: datetime):
        return value.replace(tzinfo=None)
    

    class Config:
        orm_mode = True


# Properties to return to client
class Version(VersionInDBBase):
    pass


# Properties properties stored in DB
class VersionInDB(VersionInDBBase):
    pass

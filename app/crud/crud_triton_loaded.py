from typing import List, Optional
from pydantic import UUID4

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.db.models.triton_loaded import TritonLoaded
from app.db.models.versions import Version
from app.schemas.triton_loaded import TritonLoadedUpload, TritonLoadedUpdate


class CRUDTritonLoaded(CRUDBase[TritonLoaded, TritonLoadedUpload, TritonLoadedUpdate]):
    async def get_by_version(self, db: AsyncSession, version: Version) -> Optional[TritonLoaded]:
        query = await db.execute(select(TritonLoaded).where(TritonLoaded.version_id == version.id))
        return query.scalars().first()


triton_loaded = CRUDTritonLoaded(TritonLoaded)

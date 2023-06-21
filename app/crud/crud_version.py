from typing import List, Optional
from pydantic import UUID4

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.db.models.versions import Version
from app.schemas.version import VersionUpload, VersionUpdate


class CRUDVersion(CRUDBase[Version, VersionUpload, VersionUpdate]):
    async def get(self, db: AsyncSession, id: UUID4) -> Optional[Version]:
        query = await db.execute(select(Version).where(Version.id == id).options(selectinload(Version.model)))
        return query.scalars().first()
    
    async def get_multi_by_model(
        self, db: AsyncSession, *, model_id: UUID4, skip: int = 0, limit: int = 100
    ) -> List[Version]:
        query = await db.execute(select(Version).where(Version.model_id == model_id).offset(skip).limit(limit))
        return query.scalars().all()


version = CRUDVersion(Version)

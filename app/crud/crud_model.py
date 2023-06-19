from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.db.models.models import Model
from app.schemas.model import ModelUpload, ModelUpdate

from pydantic import UUID4
from sqlalchemy import select
from typing import List, Optional


class CRUDModel(CRUDBase[Model, ModelUpload, ModelUpdate]):
    async def get(self, db: AsyncSession, id: UUID4) -> Optional[Model]:
        query = await db.execute(select(Model).where(Model.id == id).options(selectinload(Model.versions)))
        return query.scalars().first()
    
    
    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Model]:
        query = await db.execute(select(Model).options(selectinload(Model.versions)).offset(skip).limit(limit))
        return query.scalars().all()
    
    
    async def create(self, db: AsyncSession, *, obj_in: List[UploadFile]) -> Model:
        model_name = obj_in[0].filename.split("/")[0]
        db_obj = Model(
            name=model_name
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


model = CRUDModel(Model)

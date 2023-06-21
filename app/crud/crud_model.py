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

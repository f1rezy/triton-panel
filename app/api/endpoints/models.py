import os
import shutil
from typing import Any, List

import tritonclient.grpc as grpcclient
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps
from app.db.connection import get_session

router = APIRouter()


@router.get("/", response_model=List[schemas.ModelMulti])
async def get_models(
    db: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    jwt_required: bool = Depends(deps.jwt_required),
) -> Any:
    """
    Retrieve models.
    """
    models = await crud.model.get_multi(db, skip=skip, limit=limit)
    return [
        {
            "id": model.id,
            "name": model.name,
            "triton_loaded": bool(list(filter(lambda x: x.triton_loaded_version, model.versions)))
        } for model in models
    ]


@router.post("/", response_model=schemas.Model)
async def upload_model(
    *,
    db: AsyncSession = Depends(get_session),
    files: List[UploadFile] = File(title="file[]"),
    jwt_required: bool = Depends(deps.jwt_required),
) -> Any:
    """
    Upload new model.
    """
    model = await crud.model.create(db=db, obj_in=files)
    await crud.version.create(db=db, obj_in=schemas.VersionUpload(name="v1", model_id=model.id))
    
    for file in files:
        path = os.path.abspath("ml_models") + "/" + model.name + "/v1/" + "/".join(file.filename.split("/")[1:])
        dir_path = "/".join(path.split("/")[:-1])
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        with open(path, 'wb') as f:
            contents = file.file.read()
            f.write(contents)
            
    model = await crud.model.get(db=db, id=model.id)
    return model


@router.get("/{id}", response_model=schemas.Model)
async def get_model(
    *,
    db: AsyncSession = Depends(get_session),
    id: UUID4,
    jwt_required: bool = Depends(deps.jwt_required),
) -> Any:
    """
    Get model by ID.
    """
    model = await crud.model.get(db=db, id=id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.put("/{id}", response_model=schemas.Model)
async def update_model(
    *,
    db: AsyncSession = Depends(get_session),
    id: UUID4,
    files: List[UploadFile],
    jwt_required: bool = Depends(deps.jwt_required),
) -> Any:
    """
    Update an model.
    """
    model = await crud.model.get(db=db, id=id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    version = f"v{int(model.versions[-1].name[1]) + 1}"
    await crud.version.create(db=db, obj_in=schemas.VersionUpload(name=version, model_id=model.id))
    
    for file in files:
        path = os.path.abspath("ml_models") + "/" + model.name + "/" + version + "/" + \
                "/".join(file.filename.split("/")[1:])
        dir_path = "/".join(path.split("/")[:-1])
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        with open(path, 'wb') as f:
            contents = file.file.read()
            f.write(contents)
            
    await db.refresh(model)
    return model


@router.delete("/{id}", response_model=schemas.Model)
async def delete_model(
    *,
    db: AsyncSession = Depends(get_session),
    id: UUID4,
    jwt_required: bool = Depends(deps.jwt_required),
) -> Any:
    """
    Delete an model.
    """
    model = await crud.model.get(db=db, id=id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    for version in model.versions:
        await crud.version.remove(db=db, id=version.id)
        if triton_loaded := await crud.triton_loaded.get_by_version(db=db, version=version):
            triton_client = grpcclient.InferenceServerClient(url="triton:8001", verbose=False)
            triton_client.unload_model(model.name)
            path = "model_repository/" + model.name
            shutil.rmtree(path)
            
            await crud.triton_loaded.remove(db=db, id=triton_loaded.id)
    await crud.model.remove(db=db, id=id)
    shutil.rmtree("ml_models/" + model.name)

    return model

import os
import shutil
import tritonclient.grpc as grpcclient
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps
from app.db.connection import get_session

router = APIRouter()


def remove_file(filename: str):
        try:
            os.remove(filename)
        except Exception as error:
            print(error)


@router.get("/{id}", response_class=FileResponse)
async def get_version(
    *,
    db: AsyncSession = Depends(get_session),
    id: UUID4,
    jwt_required: bool = Depends(deps.jwt_required),
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Get version by ID.
    """
    version = await crud.version.get(db=db, id=id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    directory = os.path.abspath("ml_models") + "/" + version.model.name + "/" + version.name
    filename = f"{version.model.name}-{version.name}"
    shutil.make_archive(filename, 'zip', root_dir=directory)
    filename += ".zip"

    background_tasks.add_task(remove_file, filename)
    
    return os.path.abspath(filename)


@router.delete("/{id}", response_model=schemas.Version)
async def delete_version(
    *,
    db: AsyncSession = Depends(get_session),
    id: UUID4,
    jwt_required: bool = Depends(deps.jwt_required),
) -> Any:
    """
    Delete an version by ID.
    """
    version = await crud.version.get(db=db, id=id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    model = await crud.model.get(db=db, id=version.model_id)
    
    if version.triton_loaded_version:
        triton_client = grpcclient.InferenceServerClient(url="triton:8001", verbose=False)
        triton_client.unload_model(model.name)
        path = "model_repository/" + model.name
        shutil.rmtree(path)
        await crud.triton_loaded.remove(db=db, id=version.triton_loaded_version.id)
        
    await crud.version.remove(db=db, id=version.id)
    path = os.path.abspath("ml_models")
    shutil.rmtree(path + "/" + version.model.name + "/" + version.name)
    
    if not model.versions:
        await crud.model.remove(db=db, id=model.id)
        shutil.rmtree("models_onnx/" + model.name)
    
    return version
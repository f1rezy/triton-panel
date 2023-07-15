import os
import shutil
from typing import Any

import tritonclient.grpc as grpcclient
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from tritonclient.utils import InferenceServerException

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


@router.get("/{id}/config", response_model=schemas.VersionConfig)
async def get_version_config(
    *,
    db: AsyncSession = Depends(get_session),
    id: UUID4,
    jwt_required: bool = Depends(deps.jwt_required),
) -> Any:
    """
    Get version config by ID.
    """
    version = await crud.version.get(db=db, id=id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    path = f"ml_models/{version.model.name}/{version.name}/config.pbtxt"
    
    config = open(path, mode="r")
    response = schemas.VersionConfig(name=version.name, 
                                    model_id=version.model_id, 
                                    id=version.id, 
                                    upload_date=version.upload_date, 
                                    config=config.read()
                                    )
    return response


@router.post("/{id}/triton", response_model=schemas.TritonLoaded)
async def load_version_to_triton(
    *,
    db: AsyncSession = Depends(get_session),
    id: UUID4,
    jwt_required: bool = Depends(deps.jwt_required),
) -> Any:
    """
    Upload version to triton by ID.
    """
    version = await crud.version.get(db=db, id=id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    model_name = version.model.name
    source_path = "ml_models/" + model_name + "/" + version.name
    destination_path = "model_repository/" + model_name
    shutil.copytree(source_path, destination_path)

    # triton_client = grpcclient.InferenceServerClient(url="triton:8001", verbose=False)

    # try:
    #     triton_client.load_model(model_name)
    # except InferenceServerException:
    #     return HTTPException(status_code=500)
    # if not triton_client.is_model_ready(model_name):
    #     return HTTPException(status_code=500)

    triton_loaded = await crud.triton_loaded.create(db=db, obj_in=schemas.TritonLoadedUpload(version_id=version.id))
    
    return triton_loaded


@router.delete("/{id}/triton", response_model=schemas.TritonLoaded)
async def delete_version_from_triton(
    *,
    db: AsyncSession = Depends(get_session),
    id: UUID4,
    jwt_required: bool = Depends(deps.jwt_required),
) -> Any:
    """
    Delete version from triton by ID.
    """
    version = await crud.version.get(db=db, id=id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    triton_loaded = await crud.triton_loaded.get_by_version(db=db, version=version)
    if not triton_loaded:
        raise HTTPException(status_code=404, detail="Version not uploaded to triton")
    
    triton_client = grpcclient.InferenceServerClient(url="triton:8001", verbose=False)
    model_name = version.model.name
    
    try:
        triton_client.unload_model(model_name)
    except InferenceServerException:
        return HTTPException(status_code=500)
    if triton_client.is_model_ready(model_name):
        return HTTPException(status_code=500)

    path = "model_repository/" + model_name
    shutil.rmtree(path)

    await crud.triton_loaded.remove(db=db, id=triton_loaded.id)
    
    return triton_loaded

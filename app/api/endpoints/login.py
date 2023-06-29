import os
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app import schemas
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    username = form_data.username
    password = form_data.password

    if not username == os.environ.get("USERNAME", "admin") or not password == os.environ.get("PASSWORD", "admin"):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            "admin", expires_delta=access_token_expires
        ),
        "token_type": "bearer"
    }
    
    
@router.post("/login/test-token", response_model=schemas.Msg)
async def test_token(jwt_required: bool = Depends(deps.jwt_required)) -> Any:
    """
    Test access token
    """
    return {
        "msg": "Authorized"
    }

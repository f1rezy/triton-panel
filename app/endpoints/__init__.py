from .auth import bp as auth_router
from .models import bp as models_router
from .model import bp as model_router
from .triton import bp as triton_router

__all__ = [
    auth_router,
    models_router,
    model_router,
    triton_router
]

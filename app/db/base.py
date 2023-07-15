# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.models.base_class import Base  # noqa
from app.db.models.models import Model  # noqa
from app.db.models.versions import Version  # noqa
from app.db.models.triton_loaded import TritonLoaded  # noqa
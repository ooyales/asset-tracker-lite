# Import all models so SQLAlchemy can discover them for create_all()
from app.models.user import User  # noqa: F401
from app.models.asset import Asset, AssetRelationship  # noqa: F401
from app.models.people import Person  # noqa: F401
from app.models.location import Location  # noqa: F401
from app.models.security import SecurityBoundary  # noqa: F401
from app.models.license import License  # noqa: F401
from app.models.change import AssetChange  # noqa: F401
from app.models.wizard_import import WizardImport, WizardSession  # noqa: F401

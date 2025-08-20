# Import all models so Base.metadata picks them up
from .user import User  # noqa: F401
from .category import Category  # noqa: F401
from .location import Location  # noqa: F401
from .product import Product  # noqa: F401
from .inventory_item import InventoryItem  # noqa: F401
from .cost import Cost  # noqa: F401
from .webhook import Webhook  # noqa: F401

# Alias used by init_db import
all_models = True

import logging

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import get_settings
from .core.db import init_db
from .core.security import get_current_user_optional
from .middlewares.rate_limit import RateLimitMiddleware
from .routers import auth, users, products, categories, locations, inventory, costs, reporting, webhooks

# Load settings from env (.env) using pydantic-settings
settings = get_settings()

# Configure root logger
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("product-inventory-api")

app = FastAPI(
    title="Product Inventory API",
    description=(
        "Backend API for managing products, inventory, costs, categories, locations, reporting, and webhooks. "
        "Secured with JWT authentication. Auto-generated docs via FastAPI. "
        "Includes rate limiting, validation, and logging."
    ),
    version="1.0.0",
    contact={"name": "API Support"},
    license_info={"name": "MIT"},
    openapi_tags=[
        {"name": "health", "description": "Service health and info"},
        {"name": "auth", "description": "Authentication and token management"},
        {"name": "users", "description": "User management (admin only)"},
        {"name": "products", "description": "Product CRUD"},
        {"name": "categories", "description": "Category CRUD"},
        {"name": "locations", "description": "Location/Warehouse CRUD"},
        {"name": "inventory", "description": "Inventory CRUD and transfers"},
        {"name": "costs", "description": "Cost and pricing management"},
        {"name": "reporting", "description": "Reporting and analytics"},
        {"name": "webhooks", "description": "Webhook configuration and trigger endpoints"},
    ],
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(
    RateLimitMiddleware,
    rate_limit=settings.RATE_LIMIT,  # e.g., "100/minute"
    exclude_paths={"/", "/health", "/docs", "/openapi.json", "/redoc", "/auth/login", "/auth/refresh"},
)

# Initialize DB
init_db()

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(locations.router, prefix="/locations", tags=["locations"])
app.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
app.include_router(costs.router, prefix="/costs", tags=["costs"])
app.include_router(reporting.router, prefix="/reporting", tags=["reporting"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])


# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check", description="Simple health check endpoint.")
def health_check():
    """This is a public function."""
    return {"status": "healthy", "service": "Product Inventory API", "version": "1.0.0"}


# PUBLIC_INTERFACE
@app.get("/health", tags=["health"], summary="Service health details")
def health():
    """This is a public function."""
    return {"status": "ok"}


# PUBLIC_INTERFACE
@app.get("/ws-docs", tags=["health"], summary="WebSocket usage", description="This API currently exposes no WebSocket routes. Reserved for future real-time updates.")
def ws_docs():
    """This is a public function."""
    return {"message": "No WebSocket endpoints exposed at the moment."}


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    # Basic security headers
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=()"
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


# Development utility endpoint to view settings (masked)
# PUBLIC_INTERFACE
@app.get("/_config", tags=["health"], summary="View loaded configuration (masked)", include_in_schema=False)
def view_config(_: dict = Depends(get_current_user_optional), s=Depends(get_settings)):
    """This is a public function."""
    return s.masked_dict()

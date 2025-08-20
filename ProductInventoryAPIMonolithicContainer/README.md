# Product Inventory API (Monolithic FastAPI)

A monolithic FastAPI backend that provides:
- JWT Authentication (admin, manager, viewer roles)
- CRUD for Products, Categories, Locations, Inventory, Costs
- Reporting & analytics endpoints
- Webhook configuration and trigger
- Rate limiting, CORS, security headers, validation, logging
- MySQL persistence via SQLAlchemy (with SQLite fallback for local dev)
- Auto-generated docs at /docs and /redoc

## Environment variables (.env)
Create a `.env` file in the container root with:

```
# Server and logging
APP_NAME=Product Inventory API
LOG_LEVEL=INFO
CORS_ALLOW_ORIGINS=["*"]

# MySQL connection (optional for local dev; if not provided, SQLite is used)
MYSQL_HOST=
MYSQL_PORT=3306
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_DB=
# Optional SQLite fallback (default sqlite:///./inventory.db)
SQLITE_URL=sqlite:///./inventory.db

# Auth
JWT_SECRET_KEY=replace-with-strong-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Rate limiting
RATE_LIMIT=100/minute

# Webhook signing
WEBHOOK_SIGNATURE_SECRET=replace-with-strong-webhook-secret
```

Note: Never commit secrets. The orchestrator should set these in the runtime environment.

## Install & run

```
pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
```

Notes on database drivers:
- By default, this project uses SQLAlchemy with the PyMySQL driver (pure Python) for MySQL connections to ensure cross-platform, dependency-free installs in CI and local dev.
- If MYSQL_* env vars are not set, the app falls back to SQLite automatically (no external DB required).
- If you prefer the mysqlclient (C-based) driver for performance, you can replace PyMySQL with mysqlclient in requirements and set the driver URL to `mysql+mysqlclient://...`, but you must install system dependencies before pip install, e.g.:
  - Debian/Ubuntu: `apt-get update && apt-get install -y default-libmysqlclient-dev build-essential`
  - Alpine: `apk add --no-cache mariadb-connector-c-dev gcc musl-dev`
  - RHEL/CentOS/Fedora: `dnf install -y mysql-devel gcc python3-devel`

Open docs: http://localhost:3001/docs

## Initial admin
Seed an initial admin user:

POST /auth/seed-admin?username=admin&password=ChangeMe123!&email=admin@example.com

Then login at /auth/login via OAuth2 Password flow. Use returned Bearer token for protected endpoints.

## Notes
- This container uses SQLAlchemy. In production, configure MySQL env vars; for local development, the app falls back to SQLite (no external DB required).
- Rate limiting is in-memory per-process; for distributed deployments, use a shared store (e.g., Redis).
- Webhook trigger signs payloads with HMAC-SHA256 via `X-Signature`.

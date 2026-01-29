# Python Backend API Development: Golden Standards and Best Practices (2025-2026)

> A comprehensive reference for AI coding assistants and developers building production-grade Python backend APIs.

---

## Table of Contents

1. [Project Structure and Layout Conventions](#1-project-structure-and-layout-conventions)
2. [FastAPI / Flask / Django REST Best Practices](#2-fastapi--flask--django-rest-best-practices)
3. [Type Hints and Pydantic Models](#3-type-hints-and-pydantic-models)
4. [Error Handling Patterns](#4-error-handling-patterns)
5. [Database Patterns](#5-database-patterns-sqlalchemy-async-db-access)
6. [Authentication and Security](#6-authentication-and-security-oauth2-jwt)
7. [Testing](#7-testing-pytest-fixtures-mocking)
8. [Logging and Observability](#8-logging-and-observability)
9. [Dependency Injection](#9-dependency-injection)
10. [API Versioning and Documentation](#10-api-versioning-and-documentation-openapi)
11. [Async Patterns](#11-async-patterns)
12. [Code Quality Tools](#12-code-quality-tools-ruff-mypy)
13. [Environment Management](#13-environment-management-uv-poetry)
14. [Docker and Deployment Considerations](#14-docker-and-deployment-considerations)

---

## 1. Project Structure and Layout Conventions

### Guiding Principle

The best structure is one that is **consistent, straightforward, and free of surprises**. FastAPI gives you flexibility, but structure is your responsibility. The framework should be a delivery mechanism, not the center of your system.

### Small-to-Medium Projects: File-Type Based Layout

For microservices or smaller projects, organize by file type:

```
my_project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app creation, middleware, startup/shutdown
│   ├── dependencies.py      # Shared dependencies
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── items.py
│   ├── core/
│   │   ├── config.py        # Pydantic BaseSettings
│   │   └── security.py      # Auth utilities
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/              # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/             # Business logic layer
│   │   ├── __init__.py
│   │   └── user_service.py
│   └── db/
│       ├── __init__.py
│       ├── session.py        # Engine and session factory
│       └── base.py           # DeclarativeBase
├── alembic/                  # Database migrations
│   ├── versions/
│   └── env.py
├── tests/
│   ├── conftest.py
│   ├── test_users.py
│   └── test_items.py
├── alembic.ini
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── .env
```

### Large / Monolith Projects: Domain-Based Layout

For larger applications with many domains, organize by feature/domain (inspired by Netflix's Dispatch):

```
project/
├── alembic/
├── src/
│   ├── auth/
│   │   ├── router.py
│   │   ├── schemas.py        # Pydantic models for this domain
│   │   ├── models.py         # DB models for this domain
│   │   ├── dependencies.py
│   │   ├── config.py         # Domain-specific config
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── posts/
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── dependencies.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── config.py             # Global configs
│   ├── models.py             # Global/shared models
│   ├── exceptions.py         # Global exception handlers
│   ├── pagination.py         # Shared utilities
│   └── database.py           # DB engine/session
├── tests/
│   ├── auth/
│   │   └── test_auth_service.py
│   └── posts/
│       └── test_posts_service.py
├── pyproject.toml
└── Dockerfile
```

### Key Rules

- **Thin routes, fat services**: Route handlers should only do request parsing, calling services, and returning responses. Business logic lives in the `service` layer.
- **Co-locate tests with features** in larger projects so changes and tests stay synchronized.
- **Use `src/` layout** for packages intended for distribution (prevents import confusion between installed package and source).
- **One `conftest.py` per test directory** for shared fixtures.
- **Keep `main.py` lean**: Only app instantiation, middleware registration, router inclusion, and lifespan events.

---

## 2. FastAPI / Flask / Django REST Best Practices

### Framework Selection (2025 Guidance)

| Framework | Best For | Key Strength |
|-----------|----------|--------------|
| **FastAPI** | New APIs, microservices, async workloads | Performance, auto-docs, type safety, async-first |
| **Django REST Framework** | Full-featured web apps, admin-heavy projects | Batteries-included, ORM, admin, mature ecosystem |
| **Flask** | Simple APIs, legacy projects | Simplicity, flexibility, vast extension ecosystem |

**FastAPI is the recommended default for new Python API projects in 2025.** It provides automatic OpenAPI documentation, native async support, and Pydantic integration.

### FastAPI-Specific Best Practices

1. **Use `Annotated` for dependency injection** (recommended since FastAPI 0.95+):
   ```python
   from typing import Annotated
   from fastapi import Depends

   CurrentUser = Annotated[User, Depends(get_current_user)]

   @router.get("/me")
   async def read_me(user: CurrentUser):
       return user
   ```

2. **Use Pydantic `BaseSettings` for configuration**:
   ```python
   from pydantic_settings import BaseSettings

   class Settings(BaseSettings):
       database_url: str
       secret_key: str
       debug: bool = False

       model_config = ConfigDict(env_file=".env")
   ```

3. **Use lifespan events** (not deprecated `on_event`):
   ```python
   from contextlib import asynccontextmanager

   @asynccontextmanager
   async def lifespan(app: FastAPI):
       # Startup
       await init_db()
       yield
       # Shutdown
       await close_db()

   app = FastAPI(lifespan=lifespan)
   ```

4. **Use `response_model` or return type annotations** for response serialization and documentation:
   ```python
   @router.get("/users/{user_id}", response_model=UserResponse)
   async def get_user(user_id: int) -> UserResponse:
       ...
   ```

5. **Use routers with prefixes and tags**:
   ```python
   router = APIRouter(prefix="/api/v1/users", tags=["users"])
   ```

6. **Use `status` codes from `starlette`**:
   ```python
   from starlette import status

   @router.post("/users", status_code=status.HTTP_201_CREATED)
   async def create_user(...):
       ...
   ```

7. **Use middleware sparingly** -- prefer dependencies for request-scoped logic (auth, validation). Use middleware only for cross-cutting concerns (CORS, request ID, timing).

8. **Be aware of double validation**: FastAPI converts Pydantic response objects to dict, then validates against `response_model`. Avoid unnecessary overhead by aligning return types.

### Django REST Framework Key Practices

- Use `ModelSerializer` with explicit `fields` (never use `fields = "__all__"` in production).
- Use `ViewSet` + `Router` for RESTful resources.
- Use `permission_classes` and `authentication_classes` per view.
- Use `django-filter` for query filtering.
- Use `select_related` and `prefetch_related` in querysets to avoid N+1 queries.

### Flask Key Practices

- Use blueprints for modular organization.
- Use Flask-RESTful or Flask-Smorest for API structure.
- Use Flask-SQLAlchemy with proper session management.
- Use `flask.g` for request-scoped state.

---

## 3. Type Hints and Pydantic Models

### Type Hints Best Practices

1. **Use modern syntax** (Python 3.10+):
   ```python
   # Preferred (3.10+)
   def process(items: list[str], config: dict[str, int] | None = None) -> bool:
       ...

   # Avoid for new code
   from typing import List, Dict, Optional
   def process(items: List[str], config: Optional[Dict[str, int]] = None) -> bool:
       ...
   ```

2. **Type all function signatures** -- parameters and return types.

3. **Use `TypeAlias` or `type` statement (3.12+)** for complex types:
   ```python
   # Python 3.12+
   type UserID = int
   type UserMap = dict[UserID, User]

   # Python 3.10-3.11
   from typing import TypeAlias
   UserID: TypeAlias = int
   ```

4. **Use `Protocol` for structural subtyping** (duck typing with type safety):
   ```python
   from typing import Protocol

   class Repository(Protocol):
       async def get(self, id: int) -> Model: ...
       async def create(self, data: dict) -> Model: ...
   ```

5. **Use `TypeVar` and `Generic` for reusable components**:
   ```python
   from typing import TypeVar, Generic
   T = TypeVar("T")

   class PaginatedResponse(BaseModel, Generic[T]):
       items: list[T]
       total: int
       page: int
   ```

### Pydantic v2 Best Practices

1. **Separate schemas by purpose**: Create distinct models for create, update, read, and database operations:
   ```python
   class UserBase(BaseModel):
       email: EmailStr
       name: str

   class UserCreate(UserBase):
       password: str

   class UserUpdate(BaseModel):
       email: EmailStr | None = None
       name: str | None = None

   class UserResponse(UserBase):
       id: int
       created_at: datetime

       model_config = ConfigDict(from_attributes=True)
   ```

2. **Use `model_config = ConfigDict(from_attributes=True)`** (replaces `orm_mode=True` from v1) for ORM compatibility.

3. **Use `Field()` for validation and documentation**:
   ```python
   class Item(BaseModel):
       name: str = Field(..., min_length=1, max_length=100, description="Item name")
       price: float = Field(..., gt=0, description="Price in USD")
       quantity: int = Field(default=0, ge=0)
   ```

4. **Use `@field_validator` and `@model_validator`** for custom validation:
   ```python
   from pydantic import field_validator, model_validator

   class DateRange(BaseModel):
       start: date
       end: date

       @model_validator(mode="after")
       def validate_range(self) -> "DateRange":
           if self.start >= self.end:
               raise ValueError("start must be before end")
           return self
   ```

5. **Keep schemas declarative**: Do not perform database lookups or external service calls in Pydantic validators. Move those checks to FastAPI dependencies.

6. **Use `Annotated` with Pydantic types** for reusable field definitions:
   ```python
   from typing import Annotated
   from pydantic import Field

   PositiveInt = Annotated[int, Field(gt=0)]
   NonEmptyStr = Annotated[str, Field(min_length=1)]
   ```

7. **Use `model_json_schema()`** for JSON Schema generation when needed.

8. **Use `computed_field`** for derived properties in responses:
   ```python
   from pydantic import computed_field

   class UserResponse(BaseModel):
       first_name: str
       last_name: str

       @computed_field
       @property
       def full_name(self) -> str:
           return f"{self.first_name} {self.last_name}"
   ```

---

## 4. Error Handling Patterns

### Core Principles

1. **Use EAFP (Easier to Ask Forgiveness than Permission)**: Perform the action and handle errors afterward, rather than checking preconditions.

2. **Catch specific exceptions**: Never use bare `except:`. Always catch the narrowest exception class possible.

3. **Keep try blocks small and focused**: Large try blocks mask the true source of errors.

4. **Preserve tracebacks**: Use exception chaining with `raise NewError(...) from original_error`.

### API Error Handling Pattern

Define a structured error response format and custom exception hierarchy:

```python
# exceptions.py
class AppError(Exception):
    """Base application error."""
    def __init__(self, message: str, code: str, status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code

class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: str | int):
        super().__init__(
            message=f"{resource} with id '{identifier}' not found",
            code="not_found",
            status_code=404,
        )

class ValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(message=message, code="validation_error", status_code=422)

class AuthorizationError(AppError):
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message=message, code="unauthorized", status_code=403)
```

Register global exception handlers:

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )
```

### Error Response Schema

Standardize all error responses:

```python
class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None

class ErrorResponse(BaseModel):
    error: ErrorDetail
```

### Additional Patterns

- **Retry with exponential backoff**: Use `tenacity` for transient failures (network, external APIs).
- **Circuit breakers**: Use `circuitbreaker` library for persistent 5xx errors from downstream services.
- **Exception Groups (Python 3.11+)**: Use `ExceptionGroup` and `except*` for concurrent task error handling.
- **Error aggregation**: When processing batches, collect all errors and return them together rather than failing on the first.

---

## 5. Database Patterns (SQLAlchemy, Async DB Access)

### SQLAlchemy 2.0 Best Practices

1. **Use modern declarative mapping** with `Mapped` and `mapped_column`:
   ```python
   from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
   from sqlalchemy import String
   from datetime import datetime

   class Base(DeclarativeBase):
       pass

   class User(Base):
       __tablename__ = "users"

       id: Mapped[int] = mapped_column(primary_key=True)
       email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
       name: Mapped[str] = mapped_column(String(100))
       created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
       is_active: Mapped[bool] = mapped_column(default=True)
   ```

2. **Use async engine and session factory**:
   ```python
   from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

   engine = create_async_engine(
       "postgresql+asyncpg://user:pass@localhost/db",
       echo=False,
       pool_size=20,
       max_overflow=10,
   )

   async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
   ```

3. **Use a dependency for session lifecycle**:
   ```python
   async def get_db() -> AsyncGenerator[AsyncSession, None]:
       async with async_session_factory() as session:
           try:
               yield session
               await session.commit()
           except Exception:
               await session.rollback()
               raise
   ```

4. **Use `select()` style queries** (SQLAlchemy 2.0 style, not legacy `session.query()`):
   ```python
   from sqlalchemy import select

   stmt = select(User).where(User.email == email)
   result = await session.execute(stmt)
   user = result.scalar_one_or_none()
   ```

5. **Use `scalars()` for clean ORM results**:
   ```python
   result = await session.execute(select(User).where(User.is_active == True))
   users = result.scalars().all()
   ```

6. **Use write-only relationships** for async to avoid lazy loading issues:
   ```python
   from sqlalchemy.orm import WriteOnlyMapped

   class User(Base):
       posts: WriteOnlyMapped[list["Post"]] = relationship()
   ```

7. **Use `selectinload` / `joinedload`** for eager loading (avoid N+1):
   ```python
   from sqlalchemy.orm import selectinload

   stmt = select(User).options(selectinload(User.posts)).where(User.id == user_id)
   ```

### Alembic Migrations

- **Always use Alembic** for database migrations. Never use `Base.metadata.create_all()` in production.
- Use `--autogenerate` for initial migration scaffolding, but always review generated code.
- Keep migrations in version control.
- Use descriptive migration messages: `alembic revision --autogenerate -m "add_user_email_index"`

### Repository Pattern

Abstract database access behind a repository:

```python
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user
```

### Recommended Stack

- **PostgreSQL** + **asyncpg** driver for async
- **SQLAlchemy 2.0** with async extensions
- **Alembic** for migrations
- Install with `sqlalchemy[asyncio]` to include greenlet dependency

---

## 6. Authentication and Security (OAuth2, JWT)

### Architecture Decision: Build vs Buy

**Recommended approach for 2025**: Use a managed identity provider (Auth0, Clerk, AWS Cognito, Firebase Auth) for user authentication. Build only the JWT verification layer in your API. This handles password hashing, MFA, social logins, rate limiting, and compliance (HIPAA/SOC2) without custom code.

**When to build your own**: Simple internal tools, learning projects, or when vendor lock-in is unacceptable.

### JWT Best Practices

1. **Use asymmetric algorithms (RS256)** for production. Use HS256 only for simple internal services.

2. **Keep access tokens short-lived** (5-15 minutes). Use refresh tokens (hours/days) with rotation.

3. **Store minimal claims in JWT**: user ID, roles, expiration. Never store sensitive data.

4. **Always validate**:
   - Signature integrity
   - Expiration (`exp`)
   - Issuer (`iss`)
   - Audience (`aud`)

5. **Use `PyJWT`** (or `python-jose`) for token operations:
   ```python
   import jwt
   from datetime import datetime, timezone, timedelta

   def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)) -> str:
       to_encode = data.copy()
       expire = datetime.now(timezone.utc) + expires_delta
       to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
       return jwt.encode(to_encode, SECRET_KEY, algorithm="RS256")
   ```

6. **Implement token revocation** via a blocklist (Redis) for logout/security events.

### FastAPI Security Implementation

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

### Role-Based Access Control (RBAC)

```python
def require_role(required_role: str):
    def role_checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if required_role not in user.roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker

AdminUser = Annotated[User, Depends(require_role("admin"))]
```

### Additional Security Measures

- **Always use HTTPS** in production (handle via reverse proxy).
- **Configure CORS** with explicit allowed origins (never `"*"` in production).
- **Use `pwdlib`** (successor to passlib) with argon2 or bcrypt for password hashing.
- **Rate limit** authentication endpoints (use `slowapi` or reverse proxy).
- **Set secure headers** (HSTS, X-Content-Type-Options, X-Frame-Options) via middleware.
- **Validate and sanitize** all input (Pydantic handles most of this).
- **Use secrets module** for generating tokens: `import secrets; secrets.token_urlsafe(32)`.

---

## 7. Testing (pytest, Fixtures, Mocking)

### Project Test Structure

```
tests/
├── conftest.py              # Shared fixtures (db session, test client, factories)
├── unit/
│   ├── test_user_service.py
│   └── test_auth_utils.py
├── integration/
│   ├── test_user_api.py
│   └── test_database.py
└── e2e/
    └── test_user_flow.py
```

For domain-based projects, co-locate tests:
```
src/
├── auth/
│   ├── service.py
│   └── tests/
│       ├── test_service.py
│       └── test_router.py
```

### Fixture Best Practices

1. **Use `yield` for cleanup**:
   ```python
   @pytest.fixture
   async def db_session() -> AsyncGenerator[AsyncSession, None]:
       async with async_session_factory() as session:
           yield session
           await session.rollback()
   ```

2. **Scope fixtures appropriately**:
   - `scope="function"` (default): Per-test isolation, safest.
   - `scope="module"`: Share expensive setup across a module.
   - `scope="session"`: For truly expensive operations (DB engine creation).

3. **Use factory fixtures** for creating test data:
   ```python
   @pytest.fixture
   def make_user(db_session):
       async def _make_user(**kwargs) -> User:
           defaults = {"email": "test@example.com", "name": "Test User"}
           defaults.update(kwargs)
           user = User(**defaults)
           db_session.add(user)
           await db_session.flush()
           return user
       return _make_user
   ```

4. **Use `conftest.py`** for shared fixtures. Each directory can have its own `conftest.py`.

### FastAPI Test Client

```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.dependencies import get_db

@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
```

### Mocking Best Practices

1. **Use `pytest-mock`** (provides `mocker` fixture) over raw `unittest.mock`:
   ```python
   async def test_send_email(mocker):
       mock_send = mocker.patch("app.services.email.send_email", return_value=True)
       result = await notify_user(user_id=1)
       mock_send.assert_called_once()
   ```

2. **Use `autospec=True`** to ensure mocks respect function signatures:
   ```python
   mocker.patch("app.services.user.UserService", autospec=True)
   ```

3. **Use dependency overrides** in FastAPI instead of patching:
   ```python
   app.dependency_overrides[get_current_user] = lambda: mock_user
   ```

4. **Prevent real HTTP requests** with `pytest-httpx` for async or `responses` for sync:
   ```python
   # conftest.py -- block all real HTTP in tests
   @pytest.fixture(autouse=True)
   def block_real_http(monkeypatch):
       def _blocked(*args, **kwargs):
           raise RuntimeError("Real HTTP requests not allowed in tests")
       monkeypatch.setattr("httpx.AsyncClient.request", _blocked)
   ```

### General Testing Rules

- Follow the **AAA pattern**: Arrange, Act, Assert.
- Use **meaningful test names**: `test_create_user_with_duplicate_email_returns_409`.
- Keep tests **independent** -- no test should depend on another test's state.
- Use **parametrize** for testing multiple cases:
  ```python
  @pytest.mark.parametrize("email,expected", [
      ("valid@test.com", True),
      ("invalid", False),
      ("", False),
  ])
  def test_validate_email(email, expected):
      assert validate_email(email) == expected
  ```
- Use **`pytest-asyncio`** for async tests with `@pytest.mark.asyncio` or set `asyncio_mode = "auto"` in `pyproject.toml`.
- Aim for **high coverage on business logic**, not on framework boilerplate.

---

## 8. Logging and Observability

### Structured Logging with structlog

**structlog** is the recommended logging library for production Python APIs in 2025. It produces structured, machine-readable logs while remaining human-readable during development.

1. **Configure structlog with a processor pipeline**:
   ```python
   import structlog

   structlog.configure(
       processors=[
           structlog.contextvars.merge_contextvars,
           structlog.processors.add_log_level,
           structlog.processors.TimeStamper(fmt="iso"),
           structlog.processors.StackInfoRenderer(),
           structlog.processors.format_exc_info,
           # Use JSON in production, console in development
           structlog.dev.ConsoleRenderer() if settings.debug
           else structlog.processors.JSONRenderer(),
       ],
       wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
       context_class=dict,
       logger_factory=structlog.PrintLoggerFactory(),
       cache_logger_on_first_use=True,
   )
   ```

2. **Use context binding** to enrich all subsequent log entries:
   ```python
   logger = structlog.get_logger()

   # Bind context for the request
   log = logger.bind(request_id=request_id, user_id=user.id)
   log.info("processing_order", order_id=order.id)
   log.warning("low_inventory", item_id=item.id, remaining=3)
   ```

3. **Use `contextvars` for request-scoped context** (automatically propagates through async code):
   ```python
   from structlog.contextvars import bind_contextvars, clear_contextvars

   @app.middleware("http")
   async def logging_middleware(request: Request, call_next):
       clear_contextvars()
       bind_contextvars(
           request_id=str(uuid4()),
           method=request.method,
           path=request.url.path,
       )
       response = await call_next(request)
       return response
   ```

### OpenTelemetry Integration

1. **Correlate logs with traces** by adding trace/span IDs:
   ```python
   from opentelemetry import trace

   def add_otel_context(logger, method_name, event_dict):
       span = trace.get_current_span()
       if span.is_recording():
           ctx = span.get_span_context()
           event_dict["trace_id"] = format(ctx.trace_id, "032x")
           event_dict["span_id"] = format(ctx.span_id, "016x")
       return event_dict
   ```

2. **Export telemetry via OTLP** to observability backends (Datadog, Grafana, SigNoz).

3. **Instrument your application** with OpenTelemetry auto-instrumentation for FastAPI, SQLAlchemy, httpx, etc.

### Logging Rules

- **JSON format in production**, human-readable console format in development.
- **Log at appropriate levels**: DEBUG for development detail, INFO for business events, WARNING for recoverable issues, ERROR for failures, CRITICAL for system-level problems.
- **Never log sensitive data**: passwords, tokens, PII, credit card numbers.
- **Include correlation IDs** in all log entries for request tracing.
- **Use async-safe logging** to avoid blocking the event loop.
- **Implement log rotation** and set retention policies.
- **Add health check endpoints** (`/health`, `/ready`) for monitoring.
- **Export metrics** (request count, latency, error rates) via Prometheus or OpenTelemetry.

---

## 9. Dependency Injection

### FastAPI's Built-in DI System

FastAPI has a powerful, intuitive dependency injection system using `Depends()`. It is the primary mechanism for managing cross-cutting concerns.

### Patterns

1. **Function dependencies** (most common):
   ```python
   async def get_db() -> AsyncGenerator[AsyncSession, None]:
       async with async_session_factory() as session:
           yield session

   async def get_current_user(
       token: Annotated[str, Depends(oauth2_scheme)],
       db: Annotated[AsyncSession, Depends(get_db)],
   ) -> User:
       ...
   ```

2. **Class dependencies** (when you need configurable state):
   ```python
   class Pagination:
       def __init__(self, skip: int = 0, limit: int = Query(default=20, le=100)):
           self.skip = skip
           self.limit = limit
   ```

3. **Sub-dependencies / chaining** (dependencies can depend on other dependencies):
   ```python
   # get_current_user depends on get_db and oauth2_scheme
   # require_admin depends on get_current_user
   # The chain is resolved automatically
   ```

4. **Use `Annotated` type aliases** for reusable dependency declarations:
   ```python
   DB = Annotated[AsyncSession, Depends(get_db)]
   CurrentUser = Annotated[User, Depends(get_current_user)]
   AdminUser = Annotated[User, Depends(require_admin)]

   @router.get("/users")
   async def list_users(db: DB, user: AdminUser):
       ...
   ```

5. **Use dependencies for validation** (not just injection):
   ```python
   async def valid_user_id(user_id: int, db: DB) -> User:
       user = await db.get(User, user_id)
       if not user:
           raise HTTPException(status_code=404, detail="User not found")
       return user

   ValidUser = Annotated[User, Depends(valid_user_id)]

   @router.get("/users/{user_id}")
   async def get_user(user: ValidUser):
       return user
   ```

### Dependency Overrides for Testing

```python
# In tests
app.dependency_overrides[get_db] = lambda: test_db_session
app.dependency_overrides[get_current_user] = lambda: mock_admin_user
```

### Key Rules

- **Dependencies are cached per-request** by default. FastAPI will not re-execute a dependency if it has already been resolved in the same request scope.
- **Use `yield` dependencies** for resources that need cleanup (DB sessions, file handles).
- **Keep dependencies small and focused** -- decompose into multiple smaller functions rather than one large dependency.
- **Use router-level dependencies** for shared concerns like auth:
  ```python
  router = APIRouter(dependencies=[Depends(get_current_user)])
  ```

---

## 10. API Versioning and Documentation (OpenAPI)

### Versioning Strategies

**URI/Path versioning is the recommended default** for its simplicity and clarity:

```python
# Recommended: URL prefix versioning
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")
```

Other strategies (header-based, query parameter-based) are valid but less discoverable.

### Versioning Rules

- Use **Semantic Versioning (SemVer)**: MAJOR.MINOR.PATCH.
- Increment MAJOR for breaking changes.
- Increment MINOR for backward-compatible additions.
- **Run multiple major versions concurrently** to allow client migration.
- **Define a deprecation policy**: communicate timelines via response headers (`Deprecation`, `Sunset`) and documentation.
- **Avoid breaking changes** wherever possible -- prefer additive changes (new fields, new endpoints).

### OpenAPI / Swagger Documentation

FastAPI generates OpenAPI documentation automatically. Enhance it:

1. **Add metadata to your app**:
   ```python
   app = FastAPI(
       title="My API",
       description="Production API for managing resources",
       version="1.0.0",
       docs_url="/docs",       # Swagger UI
       redoc_url="/redoc",     # ReDoc
   )
   ```

2. **Document every endpoint** with summaries, descriptions, and response models:
   ```python
   @router.post(
       "/users",
       response_model=UserResponse,
       status_code=201,
       summary="Create a new user",
       description="Creates a new user account with the provided details.",
       responses={
           409: {"model": ErrorResponse, "description": "Email already exists"},
           422: {"model": ErrorResponse, "description": "Validation error"},
       },
   )
   ```

3. **Use tags** to organize endpoints by domain.

4. **Document authentication** requirements in the OpenAPI spec.

5. **Version-control your OpenAPI spec** alongside your code.

6. **Use `examples` in Pydantic models** for better documentation:
   ```python
   class UserCreate(BaseModel):
       email: EmailStr
       name: str

       model_config = ConfigDict(json_schema_extra={
           "examples": [
               {"email": "user@example.com", "name": "Jane Doe"}
           ]
       })
   ```

---

## 11. Async Patterns

### When to Use Async

| Use Async | Use Sync (or `to_thread`) |
|-----------|---------------------------|
| HTTP calls to external APIs | CPU-bound computation |
| Database queries (with async driver) | Image/video processing |
| File I/O (with `aiofiles`) | ML inference |
| WebSocket connections | Heavy data crunching |
| Queue operations | Legacy blocking libraries |

### Key Patterns

1. **Use `async def` for I/O-bound routes; `def` for CPU-bound**:
   ```python
   # I/O-bound: use async
   @router.get("/users")
   async def list_users(db: DB):
       result = await db.execute(select(User))
       return result.scalars().all()

   # CPU-bound: use sync (FastAPI runs in threadpool)
   @router.get("/report")
   def generate_report():
       return compute_heavy_report()
   ```

2. **Never run blocking code in async routes**. If you must call blocking code from async context:
   ```python
   import asyncio

   result = await asyncio.to_thread(blocking_function, arg1, arg2)
   ```

3. **Use `asyncio.gather()` for concurrent I/O**:
   ```python
   user, orders, notifications = await asyncio.gather(
       get_user(user_id),
       get_orders(user_id),
       get_notifications(user_id),
   )
   ```

4. **Use `TaskGroup` (Python 3.11+)** for structured concurrency with proper error handling:
   ```python
   async with asyncio.TaskGroup() as tg:
       task1 = tg.create_task(fetch_user(user_id))
       task2 = tg.create_task(fetch_permissions(user_id))
   # Both tasks guaranteed complete (or all cancelled on error)
   user = task1.result()
   perms = task2.result()
   ```

5. **Use semaphores for rate limiting** concurrent operations:
   ```python
   semaphore = asyncio.Semaphore(10)  # Max 10 concurrent

   async def rate_limited_fetch(url: str):
       async with semaphore:
           return await client.get(url)
   ```

6. **Use long-lived async clients** (do not create per request):
   ```python
   # In lifespan
   @asynccontextmanager
   async def lifespan(app: FastAPI):
       app.state.http_client = httpx.AsyncClient()
       yield
       await app.state.http_client.aclose()
   ```

7. **Use `asyncio.Queue`** for producer/consumer patterns within a service.

### Common Pitfalls

- **Do not use `requests`** in async code. Use `httpx.AsyncClient`.
- **Do not use `time.sleep()`** in async code. Use `asyncio.sleep()`.
- **Do not forget `await`** -- a missing `await` causes "coroutine was never awaited" warnings.
- **Do not use synchronous database drivers** in async routes.
- **Do not block the event loop** with CPU-heavy work -- offload to `asyncio.to_thread()` or a process pool.

---

## 12. Code Quality Tools (Ruff, Mypy)

### The Modern Python Quality Stack (2025)

| Tool | Purpose | Replaces |
|------|---------|----------|
| **Ruff** | Linting + formatting | flake8, black, isort, pyupgrade, autoflake, pylint (partially) |
| **Mypy** (or Pyright) | Static type checking | - (not replaceable by Ruff) |
| **Bandit** | Security scanning | - |
| **pre-commit** | Git hook automation | - |

### Ruff Configuration

```toml
# pyproject.toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # pyflakes
    "I",     # isort
    "N",     # pep8-naming
    "UP",    # pyupgrade
    "B",     # flake8-bugbear
    "SIM",   # flake8-simplify
    "TCH",   # flake8-type-checking
    "RUF",   # ruff-specific rules
    "ASYNC", # flake8-async
    "S",     # flake8-bandit (security)
    "PTH",   # flake8-use-pathlib
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.lint.isort]
known-first-party = ["app"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### Mypy Configuration

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
strict = true                        # Enable all strict checks
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
plugins = ["pydantic.mypy", "sqlalchemy.ext.mypy.plugin"]

[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false        # Relax strictness for tests
```

For existing codebases, start without `strict = true` and enable checks incrementally.

### Development Workflow

```bash
# Lint (with auto-fix)
ruff check . --fix

# Format
ruff format .

# Type check
mypy .

# Security scan
bandit -r app/
```

### Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, sqlalchemy]
```

### CI Integration

Run all quality checks in CI on every push/PR. Fail the build if any check fails. This is non-negotiable for production codebases.

---

## 13. Environment Management (uv, Poetry)

### Recommendation for 2025

**Use `uv` for new projects.** It is the fastest Python package manager (10-100x faster than pip/Poetry), written in Rust by Astral (same team as Ruff). It replaces pip, pip-tools, pipx, virtualenv, and pyenv in a single binary.

**Use Poetry** if you are maintaining an existing Poetry-based project, publishing libraries to PyPI, or if your team requires the maturity of a 6+ year-old tool.

### uv Workflow

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create a new project
uv init my-api
cd my-api

# Add dependencies
uv add fastapi uvicorn sqlalchemy[asyncio] asyncpg pydantic-settings

# Add dev dependencies
uv add --dev pytest pytest-asyncio pytest-mock httpx ruff mypy

# Run your app
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest

# Sync from lockfile (CI/CD)
uv sync
```

### uv Key Features

- **`uv.lock`**: Reproducible, cross-platform lockfile (always commit this).
- **`pyproject.toml`**: All configuration in one file.
- **Python version management**: Set `.python-version` file; `uv run` automatically installs the right Python.
- **Global cache**: Packages are downloaded once and linked across projects (saves disk space).
- **Workspaces**: Native monorepo support.

### pyproject.toml (uv-based project)

```toml
[project]
name = "my-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.30",
    "pydantic-settings>=2.6",
    "alembic>=1.14",
    "structlog>=24.4",
    "pyjwt[crypto]>=2.9",
    "httpx>=0.28",
]

[dependency-groups]
dev = [
    "pytest>=8.3",
    "pytest-asyncio>=0.24",
    "pytest-mock>=3.14",
    "pytest-cov>=6.0",
    "ruff>=0.8",
    "mypy>=1.13",
    "pre-commit>=4.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
target-version = "py312"
line-length = 120
```

### Poetry Workflow (for existing projects)

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Create project
poetry new my-api
cd my-api

# Add dependencies
poetry add fastapi uvicorn sqlalchemy asyncpg

# Add dev dependencies
poetry add --group dev pytest ruff mypy

# Run
poetry run uvicorn app.main:app --reload

# Install from lockfile
poetry install --no-interaction
```

---

## 14. Docker and Deployment Considerations

### Dockerfile Best Practices

```dockerfile
# syntax=docker/dockerfile:1

# ---- Builder Stage ----
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

# ---- Production Stage ----
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --no-create-home appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Switch to non-root user
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose (Development)

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app/app  # Hot reload in dev
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Production Deployment Rules

1. **Use multi-stage builds** to minimize image size. Production images should not contain build tools, dev dependencies, or source code that is not needed.

2. **Run as non-root user** -- never run containers as root in production.

3. **Use slim base images**: `python:3.12-slim-bookworm` not `python:3.12`.

4. **Set environment variables**:
   - `PYTHONDONTWRITEBYTECODE=1` -- prevents `.pyc` files.
   - `PYTHONUNBUFFERED=1` -- ensures logs appear immediately.

5. **Order Dockerfile layers** for cache efficiency: system deps -> Python deps -> application code.

6. **One process per container** when using Kubernetes or similar orchestrators. Let the orchestrator handle scaling.

7. **Use Gunicorn + Uvicorn workers** when NOT using container orchestration:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```
   Worker count formula: `(2 * CPU_CORES) + 1`.

8. **Use a reverse proxy** (Nginx, Traefik, Caddy) for:
   - TLS termination / HTTPS
   - Static file serving
   - Load balancing
   - Rate limiting

9. **Implement health checks**: `/health` (liveness) and `/ready` (readiness, checks DB connectivity).

10. **Run database migrations** as a separate step (init container in K8s, or pre-deploy command), not at application startup:
    ```bash
    alembic upgrade head
    ```

11. **Use `.dockerignore`** to exclude unnecessary files:
    ```
    .git
    .venv
    __pycache__
    *.pyc
    .env
    tests/
    .mypy_cache
    .ruff_cache
    ```

12. **Scan images for vulnerabilities**: Use `docker scout`, `trivy`, or `snyk`.

### CI/CD Pipeline

A typical pipeline:

1. **Lint & Format**: `ruff check . && ruff format --check .`
2. **Type Check**: `mypy .`
3. **Test**: `pytest --cov=app --cov-report=xml`
4. **Security Scan**: `bandit -r app/ && safety check`
5. **Build Docker Image**: `docker build -t myapp:$SHA .`
6. **Push to Registry**: `docker push registry/myapp:$SHA`
7. **Deploy**: Update Kubernetes manifest / trigger deployment

---

## Summary: The 2025 Python API Stack

| Layer | Recommended Tool |
|-------|-----------------|
| **Framework** | FastAPI |
| **Python Version** | 3.12+ |
| **Package Manager** | uv |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Database** | PostgreSQL + asyncpg |
| **Migrations** | Alembic |
| **Validation** | Pydantic v2 |
| **Auth** | PyJWT + managed IdP (Auth0/Clerk) |
| **HTTP Client** | httpx (async) |
| **Logging** | structlog |
| **Observability** | OpenTelemetry |
| **Linting/Formatting** | Ruff |
| **Type Checking** | Mypy (strict) |
| **Testing** | pytest + pytest-asyncio + pytest-mock |
| **Containerization** | Docker (multi-stage, slim, non-root) |
| **ASGI Server** | Uvicorn (+ Gunicorn for process management) |
| **Reverse Proxy** | Nginx / Traefik / Caddy |

---

## Sources

- [FastAPI Best Practices - zhanymkanov (GitHub)](https://github.com/zhanymkanov/fastapi-best-practices)
- [Structuring a FastAPI Project - DEV Community](https://dev.to/mohammad222pr/structuring-a-fastapi-project-best-practices-53l6)
- [FastAPI Official Documentation](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [How to Structure a Scalable FastAPI Project - FastLaunchAPI](https://fastlaunchapi.dev/blog/how-to-structure-fastapi)
- [Building Production-Ready FastAPI Applications with Service Layer Architecture](https://medium.com/@abhinav.dobhal/building-production-ready-fastapi-applications-with-service-layer-architecture-in-2025-f3af8a6ac563)
- [Pydantic Best Practices for FastAPI Applications](https://www.kevsrobots.com/learn/pydantic/11_performance_optimization_tips.html)
- [The Ultimate Guide to Error Handling in Python - Miguel Grinberg](https://blog.miguelgrinberg.com/post/the-ultimate-guide-to-error-handling-in-python)
- [5 Error Handling Patterns in Python - KDnuggets](https://www.kdnuggets.com/5-error-handling-patterns-in-python-beyond-try-except)
- [10 SQLAlchemy 2.0 Patterns for Clean Async Postgres](https://medium.com/@ThinkingLoop/10-sqlalchemy-2-0-patterns-for-clean-async-postgres-af8c4bcd86fe)
- [SQLAlchemy 2.0 Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Patterns and Practices for SQLAlchemy 2.0 with FastAPI](https://chaoticengineer.hashnode.dev/fastapi-sqlalchemy)
- [Mastering API Security in 2025 - JWT, OAuth2, Rate Limiting](https://medium.com/@priyaranjanpatraa/mastering-api-security-in-2025-jwt-oauth2-rate-limiting-best-practices-cecf96568025)
- [FastAPI Security - OAuth2 with JWT (Official)](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Authentication and Authorization with FastAPI - Better Stack](https://betterstack.com/community/guides/scaling-python/authentication-fastapi/)
- [How to Handle JWT Authentication Securely in Python](https://oneuptime.com/blog/post/2025-01-06-python-jwt-authentication/view)
- [Testing APIs with PyTest - CodiLime](https://codilime.com/blog/testing-apis-with-pytest-mocks-in-python/)
- [Mastering Pytest: Advanced Fixtures, Parameterization, and Mocking](https://medium.com/@abhayda/mastering-pytest-advanced-fixtures-parameterization-and-mocking-explained-108a7a2ab82d)
- [Python Logging with Structlog - Last9](https://last9.io/blog/python-logging-with-structlog/)
- [Python Structured Logging with OpenTelemetry](https://oneuptime.com/blog/post/2025-01-06-python-structured-logging-opentelemetry/view)
- [Leveling Up Python Logs with Structlog - Dash0](https://www.dash0.com/guides/python-logging-with-structlog)
- [Mastering Dependency Injection in FastAPI](https://medium.com/@azizmarzouki/mastering-dependency-injection-in-fastapi-clean-scalable-and-testable-apis-5f78099c3362)
- [FastAPI Dependencies (Official)](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [API Versioning Best Practices - Redocly](https://redocly.com/blog/api-versioning-best-practices)
- [API Documentation Best Practices 2025 - Theneo](https://www.theneo.io/blog/api-documentation-best-practices-guide-2025)
- [Async APIs with FastAPI: Patterns, Pitfalls & Best Practices](https://shiladityamajumder.medium.com/async-apis-with-fastapi-patterns-pitfalls-best-practices-2d72b2b66f25)
- [Asyncio Design Patterns - dev-kit.io](https://dev-kit.io/blog/python/asyncio-design-patterns)
- [Modern Python Code Quality Setup: uv, ruff, and mypy](https://simone-carolini.medium.com/modern-python-code-quality-setup-uv-ruff-and-mypy-8038c6549dcc)
- [A Modern Python Toolkit: Pydantic, Ruff, MyPy, and UV](https://dev.to/devasservice/a-modern-python-toolkit-pydantic-ruff-mypy-and-uv-4b2f)
- [Ruff FAQ (Official)](https://docs.astral.sh/ruff/faq/)
- [Python UV: The Ultimate Guide - DataCamp](https://www.datacamp.com/tutorial/python-uv)
- [Poetry vs UV - Which Python Package Manager in 2025](https://medium.com/@hitorunajp/poetry-vs-uv-which-python-package-manager-should-you-use-in-2025-4212cb5e0a14)
- [uv Official Documentation](https://docs.astral.sh/uv/)
- [FastAPI Docker Best Practices - Better Stack](https://betterstack.com/community/guides/scaling-python/fastapi-docker-best-practices/)
- [FastAPI in Containers - Docker (Official)](https://fastapi.tiangolo.com/deployment/docker/)
- [FastAPI Production Deployment 2025 - CYS Docs](https://craftyourstartup.com/cys-docs/fastapi-production-deployment/)

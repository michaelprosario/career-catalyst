# Clean Architecture Rules for Python (Ardalis/Steven Smith)

## Core Principles

### 1. Dependency Rule
- Dependencies must point **inward** toward the center (Domain)
- Inner layers cannot depend on outer layers
- Domain layer has **zero dependencies** on external frameworks
- Use **Dependency Inversion** through abstract base classes and protocols

### 2. Layer Structure (Inside-Out)
```
Domain (Core) → Application (Use Cases) → Infrastructure → Presentation
```

## Layer-Specific Rules

### Domain Layer (Core Business Logic)
**What belongs here:**
- Business entities and value objects
- Domain services and business rules
- Domain events and specifications
- Custom exceptions for business rule violations

**Rules:**
- ✅ **NO external dependencies** (no imports from other layers)
- ✅ Pure Python classes with business logic only
- ✅ Use `dataclasses`, `Pydantic models`, or plain classes for entities
- ✅ Define abstract interfaces using `ABC` and `Protocol`
- ❌ NO framework dependencies (FastAPI, Django, SQLAlchemy, etc.)
- ❌ NO infrastructure concerns (databases, HTTP, file I/O)

**Python Structure:**
```python
# domain/entities/user.py
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class User:
    id: str
    email: str
    
    def change_email(self, new_email: str) -> None:
        # Business rule validation
        pass

# domain/interfaces/user_repository.py
class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None:
        pass
```

### Application Layer (Use Cases/Services)
**What belongs here:**
- Use case implementations
- Application services
- Command/Query handlers
- DTOs and application-specific models
- Orchestration logic

**Rules:**
- ✅ Can depend on Domain layer
- ✅ Define interfaces for infrastructure dependencies
- ✅ Use dependency injection for external services
- ✅ Handle cross-cutting concerns (logging, validation, caching)
- ❌ NO direct infrastructure dependencies
- ❌ NO framework-specific code
- ❌ NO database or HTTP concerns

**Python Structure:**
```python
# application/services/user_service.py
from domain.interfaces.user_repository import IUserRepository
from domain.entities.user import User

class UserService:
    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo
    
    async def create_user(self, email: str) -> User:
        # Use case logic here
        pass
```

### Infrastructure Layer (External Concerns)
**What belongs here:**
- Database implementations (SQLAlchemy, MongoDB, etc.)
- External API clients
- File system operations
- Email services, message queues
- Framework configurations

**Rules:**
- ✅ Can depend on Domain and Application layers
- ✅ Implements interfaces defined in inner layers
- ✅ Contains all framework-specific code
- ✅ Handles data persistence and external integrations
- ❌ Business logic should NOT live here
- ❌ Should not contain use case orchestration

**Python Structure:**
```python
# infrastructure/repositories/sqlalchemy_user_repository.py
from sqlalchemy.orm import Session
from domain.interfaces.user_repository import IUserRepository
from domain.entities.user import User

class SqlAlchemyUserRepository(IUserRepository):
    def __init__(self, session: Session):
        self._session = session
    
    async def get_by_id(self, user_id: str) -> User | None:
        # SQLAlchemy implementation
        pass
```

### Presentation Layer (Controllers/APIs)
**What belongs here:**
- FastAPI/Django controllers
- Request/Response models
- Authentication/Authorization
- Input validation and serialization
- HTTP-specific logic

**Rules:**
- ✅ Can depend on Application layer (through interfaces)
- ✅ Handle HTTP concerns (routing, serialization, status codes)
- ✅ Input validation and transformation
- ✅ Authentication and authorization
- ❌ NO business logic
- ❌ NO direct database access
- ❌ Should not depend on Infrastructure layer directly

**Python Structure:**
```python
# presentation/api/user_controller.py
from fastapi import APIRouter, Depends
from application.services.user_service import UserService

router = APIRouter()

@router.post("/users")
async def create_user(
    request: CreateUserRequest,
    user_service: UserService = Depends()
):
    # Controller logic only
    pass
```

## Python-Specific Implementation Guidelines

### 1. Dependency Injection
```python
# Use dependency-injector or similar
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    # Infrastructure
    db_session = providers.Singleton(create_db_session)
    
    # Repositories
    user_repository = providers.Factory(
        SqlAlchemyUserRepository,
        session=db_session
    )
    
    # Services
    user_service = providers.Factory(
        UserService,
        user_repo=user_repository
    )
```

### 2. Abstract Base Classes and Protocols
```python
# Use ABC for strict contracts
from abc import ABC, abstractmethod

class IUserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> None: ...

# Use Protocol for structural typing
from typing import Protocol

class UserRepositoryProtocol(Protocol):
    async def save(self, user: User) -> None: ...
```

### 3. Package Structure
```
src/
├── domain/
│   ├── entities/
│   ├── interfaces/
│   ├── services/
│   └── exceptions/
├── application/
│   ├── services/
│   ├── dtos/
│   └── interfaces/
├── infrastructure/
│   ├── repositories/
│   ├── external_services/
│   ├── persistence/
│   └── configuration/
├── presentation/
│   ├── api/
│   ├── schemas/
│   └── middleware/
└── main.py
```

### 4. Testing Strategy
```python
# Domain tests - Pure unit tests
def test_user_change_email():
    user = User(id="1", email="old@email.com")
    user.change_email("new@email.com")
    assert user.email == "new@email.com"

# Application tests - Use mocks for dependencies
@pytest.fixture
def mock_user_repo():
    return Mock(spec=IUserRepository)

def test_create_user_service(mock_user_repo):
    service = UserService(mock_user_repo)
    # Test use case logic
```

## Key Python Adaptations

1. **Use `dataclasses` or `Pydantic`** for entities instead of complex ORM models in domain
2. **Leverage `typing` module** for interface definitions and type hints
3. **Use `ABC` and `Protocol`** for defining contracts
4. **Implement dependency injection** using libraries like `dependency-injector`
5. **Separate SQLAlchemy models** from domain entities (keep them in infrastructure)
6. **Use async/await** patterns consistently across layers when needed
7. **Leverage Python's module system** for clean package organization

## Validation Rules Checklist

- [ ] Domain entities have no external dependencies
- [ ] Application services only depend on domain interfaces
- [ ] Infrastructure implements domain/application interfaces
- [ ] Presentation layer doesn't contain business logic
- [ ] Dependencies point inward only
- [ ] Each layer has a single, well-defined responsibility
- [ ] Tests can be written for each layer in isolation
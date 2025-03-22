# Technical Context

## Technology Stack

- **Python 3.13.2** - The programming language used for this project
- **Poetry** - Dependency management
- **FastAPI** - Web framework for building APIs
- **SQLAlchemy** - ORM with Declarative syntax using DeclarativeBase
- **SQLite** - Database
- **Pydantic** - Data validation and settings management
- **JWT** - Authentication
- **bcrypt** - Password hashing

## Development Setup

The project uses Poetry for dependency management and pyenv for Python version management. The required Python version is 3.13.2 as specified in the `.python-version` file.

## Key Dependencies

The project will depend on the following packages:
- `fastapi` - High-performance web framework
- `sqlalchemy` - SQL toolkit and ORM
- `pydantic` - Data validation
- `uvicorn` - ASGI server for running the API
- `python-jose` - For JWT token handling
- `passlib[bcrypt]` - For password hashing
- `aiosqlite` - Async SQLite driver

## Technical Constraints

- We need to store monetary amounts as integers (cents) to avoid floating-point precision issues
- All database timestamps should be stored in milliseconds (UNIX timestamp * 1000)
- The SQLite database should be properly configured for asynchronous access
# Worthy api

## How to start

### Setup

```bash
# Setup python

pyenv install 3.13.2
# if it already exists dont install

pyenv local 3.13.2
# check with python --version

# Setup poetry

# check if it's already installed 
poetry -V
# should output "Poetry (version 2.1.1)"

# if not installed
curl -sSL https://install.python-poetry.org | python3 -

# Activate poetry env
eval $(poetry env activate)

# U are ready to go :)
```

### Run project

```shell
poetry install
poetry run python run.py
```

## Tech Stack

- pyenv
- poetry
- fastapi
- sqlalchemy (Declarative syntax, with DeclarativeBase)

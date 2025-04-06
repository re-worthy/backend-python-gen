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


# TODO

- [x] (architecture) repository classes: apllication should use technique called repository classes to abstract data retrieval and management
- [ ] (feature) transcation groups: there should be a way to combine several transactions into a group, that would be displayed on frontend.
- [ ] (feature) templates: there should be a way template transactions and CRUD operations around it
- [ ] (feature) openapi.json: there should be a route to get current openapi spec in json format

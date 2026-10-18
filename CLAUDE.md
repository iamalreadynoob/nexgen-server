# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Nexgen Server is a FastAPI + MongoDB (async PyMongo) API that stores **actuators**: versioned, named Python methods (`actuator_type` is `coding` or `decoding`), with their source code and `requirements`. For each `name`, exactly one active version should have `latest: True`. `app/schemas/data.py` is a draft schema for data items produced by actuators; it is not wired up to anything yet.

## Commands

Python 3.12. Dependencies are managed with `uv` (`pyproject.toml` / `uv.lock`). The Docker image installs from `requirements.txt` instead, and only that file lists `uvicorn` and `gunicorn`, so keep the two in sync when adding dependencies.

```bash
uv sync                                   # install deps into .venv
uv run uvicorn app.main:app --reload      # dev server (needs a reachable MongoDB)
uv run ruff check .                       # lint (--fix to autofix)
uv run ruff format .                      # format
uv run pre-commit run --all-files         # hygiene hooks + ruff, same as on commit
docker compose up --build                 # API + mongo:7; reads .env
```

```bash
uv run pytest                             # all tests (no MongoDB needed)
uv run pytest tests/unit/api -k create    # a subset
uv run pytest --cov                       # with coverage
```

Swagger UI is at `/docs` unless `ENVIRONMENT=production`.

## Tests

`tests/` mirrors `app/` under `unit/` (later `integration/`). Test deps are in the uv `dev` group, never in `requirements.txt`. Starlette's `TestClient` needs `httpx2`, not `httpx`; `filterwarnings = error` turns the deprecation into a failure.
- `tests/conftest.py`: `settings` (built with `_env_file=None`, so `.env` is ignored), `app` (fresh `create_app()` per test, overrides cleared after), `client` (sends `X-API-Key`), `anon_client`, `actuator_factory`, and `data_factory`.
- The `TestClient` is never entered as a context manager, so the lifespan (the Mongo client and file logging) does not run.
- Endpoint tests replace the service with `create_autospec(Service, instance=True)` through `app.dependency_overrides[get_<x>_service]`, then assert status codes, response JSON and `assert_awaited_once_with(...)`. Responses render with aliases, so `ActuatorOut` comes back as `_id`, not `id`.
- `.github/workflows/ci.yml` runs ruff (check and format) and pytest on every push and on PRs to `main`. The `test` job is a matrix with one job per suite (`actuators`, `data`), each running the files in its `paths`; a new test module must be added to a suite's `paths`, or CI will not run it.

## Configuration

`app/core/config.py` (pydantic-settings) reads environment variables or `.env`. `.env.tmp` is the template. Key settings:
- `API_KEY`: a comma-separated list of keys. Empty, unset, or `none`/`null`/`false`/`disabled` turns auth **off** and leaves the API open.
- `MONGODB_URI` and `MONGODB_DB` (default `nexgen`). docker-compose builds `MONGODB_URI` itself from `MONGO_ROOT_USERNAME`/`MONGO_ROOT_PASSWORD`.
- `get_settings()` is cached with `lru_cache`.

## Architecture

The code is split into layers, wired through FastAPI `Depends` in `app/api/deps.py`:

`endpoints (app/api/v1/endpoints)` → `service (app/services)` → `repository (app/repositories)` → Mongo collection

- **Endpoints** are thin. They pass query and path params through to the service.
- **Services** hold the business rules: uniqueness of name+version and latest-flag handling. They raise `NotFoundError` / `AlreadyExistsError` from `app/core/exceptions.py`, which global handlers turn into HTTP responses. Services return Pydantic models through `Model.model_validate(doc)`.
- **Repositories** own every Mongo query and return raw dicts. String IDs are converted with `_oid()`, which returns `None` for an invalid ObjectId; callers treat that as not found.
- **Mongo client**: one `AsyncMongoClient` per process, created in the `lifespan` in `app/main.py` and stored on `app.state.db`. `get_database` reads it from the request.
- **Auth**: `app/api/v1/router.py` attaches `verify_api_key` (the `X-API-Key` header, compared in constant time) to a `protected` router. New protected endpoint modules go into `protected.include_router(...)`. Public ones, like health, go directly on `api_router`. Everything is mounted under `/api/v1`.
- **Soft delete**: deleting sets `active: False`. Repository queries filter on `active: True`.
- **Schemas**: `ActuatorOut.id` takes its value from Mongo's `_id` through `alias="_id"`, and `PyObjectId` converts it to a string. Clients send `set_latest` on create, and the service turns it into the stored `latest` field.
- `app/main.py` middleware sets or propagates an `X-Request-ID` header and logs each request. Logs go to stdout and a rotating `app.log` in the working directory.

## Conventions

Ruff config in `pyproject.toml` is strict (pydocstyle with the Google convention, annotations, bandit, and more). Every module, class, and function needs a docstring. The existing code uses titles such as `"""# Get Actuator."""`. Endpoint functions return untyped values and carry `# noqa: ANN201`. Multi-line calls use trailing commas, and keyword arguments are passed explicitly, even with a single argument.

# Development

This document explains how to run the tests and the linters, how CI works, and which code conventions to follow.

## Environment

1. Install Python 3.12 and [uv](https://github.com/astral-sh/uv).
2. Install the dependencies, including the `dev` group:

   ```bash
   uv sync
   ```

3. Install the pre-commit hooks:

   ```bash
   uv run pre-commit install
   ```

## Dependencies

The project has two dependency lists:

- `pyproject.toml` and `uv.lock` are for uv.
- `requirements.txt` is for the Docker image. Only this file lists `uvicorn` and `gunicorn`.

When you add a runtime dependency, add it to both lists. Put test dependencies only in the uv `dev` group, never in `requirements.txt`.

## Tests

The tests do not need MongoDB.

```bash
uv run pytest                             # all tests
uv run pytest tests/unit/api -k create    # a subset
uv run pytest --cov                       # with coverage
```

### Test layout

`tests/` has the same structure as `app/`, under `unit/`.

[`tests/conftest.py`](../tests/conftest.py) gives these fixtures:

| Fixture | Description |
|---|---|
| `settings` | Settings with a test API key. It ignores `.env`. |
| `app` | A new app from `create_app()` for each test. The fixture clears the dependency overrides after the test. |
| `client` | A `TestClient` that sends the `X-API-Key` header |
| `anon_client` | A `TestClient` with no API key |
| `actuator_factory`, `data_factory`, `content_factory` | Functions that make response objects for the tests |

### How endpoint tests work

1. The test makes a mock service with `create_autospec(Service, instance=True)`.
2. The test puts the mock into `app.dependency_overrides[get_<x>_service]`.
3. The test sends a request with `client`.
4. The test checks the status code, the response JSON and `assert_awaited_once_with(...)`.

The `TestClient` is not used as a context manager. Thus the lifespan does not run, and the tests do not connect to MongoDB.

Responses use the field aliases. An actuator comes back with `_id`, not `id`.

### Test client dependency

The Starlette `TestClient` needs `httpx2`, not `httpx`. The pytest setting `filterwarnings = error` changes each warning into a test failure, including the `httpx` deprecation warning.

## Lint and format

```bash
uv run ruff check .                # lint
uv run ruff check . --fix          # lint and fix
uv run ruff format .               # format
uv run pre-commit run --all-files  # all hooks, as on commit
```

The pre-commit hooks check YAML, TOML and JSON files, merge conflicts, large files and private keys. They also run Ruff.

## Continuous integration

[`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs on each push and on each pull request to `main`.

| Job | Steps |
|---|---|
| `lint` | `ruff check` and `ruff format --check` |
| `test` | One job for each suite: `actuators`, `data` and `contents`. Each job runs the test files in its `paths`. |

> [!IMPORTANT]
> When you add a test module, add it to the `paths` of a suite in `ci.yml`. If you do not, CI does not run it.

## Code conventions

- The Ruff configuration is strict. It includes pydocstyle (Google convention), annotations and bandit rules.
- Each module, class and function needs a docstring. The existing code uses titles such as `"""# Get Actuator."""`.
- Endpoint functions return untyped values and have `# noqa: ANN201`.
- Multi-line calls use trailing commas.
- Pass keyword arguments explicitly, also when there is only one argument.

## Add a new endpoint module

1. Add the schemas in `app/schemas/`.
2. Add the repository in `app/repositories/`. Put all MongoDB queries there.
3. Add the service in `app/services/`. Put the business rules there, and raise the errors from `app/core/exceptions.py`.
4. Add a `get_<x>_service` function in `app/api/deps.py`.
5. Add the router in `app/api/v1/endpoints/`. Keep the endpoint functions thin.
6. Add the router in `app/api/v1/router.py`. Use `protected.include_router(...)` for a protected module, or `api_router.include_router(...)` for a public module.
7. Add the tests in `tests/unit/api/v1/`, and add the file to a suite in `ci.yml`.
8. Add an API document in `docs/api/`, and add a link in the [README](../README.md#documentation).

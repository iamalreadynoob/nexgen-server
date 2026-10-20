# Configuration

Nexgen Server reads its settings from environment variables or from a `.env` file in the working directory. [`app/core/config.py`](../app/core/config.py) defines the settings. [`.env.tmp`](../.env.tmp) is the template.

## Settings

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `Nexgen Server` | The title of the API in the OpenAPI document |
| `ENVIRONMENT` | `development` | If the value is `production`, the server does not show `/docs`. |
| `LOG_LEVEL` | `INFO` | The log level, for example `DEBUG`, `INFO` or `WARNING` |
| `API_KEY` | not set | A comma-separated list of valid API keys. See [Authentication](#authentication). |
| `MONGODB_URI` | `mongodb://localhost:27017` | The MongoDB connection string |
| `MONGODB_DB` | `nexgen` | The database name |
| `MONGODB_MAX_POOL_SIZE` | `100` | The maximum size of the connection pool. It must be 1 or more. |
| `MONGODB_MIN_POOL_SIZE` | `0` | The minimum size of the connection pool. It must be 0 or more. |

The names are not case-sensitive. The server ignores unknown variables.

The server reads the settings one time for each process. To apply a change, restart the server.

### Docker Compose variables

[`docker-compose.yaml`](../docker-compose.yaml) also uses these variables:

| Variable | Description |
|---|---|
| `MONGO_ROOT_USERNAME` | The MongoDB root user. It is necessary. |
| `MONGO_ROOT_PASSWORD` | The MongoDB root password. It is necessary. |
| `API_PORT` | The host port for the API. The default is `8000`. |

Docker Compose makes `MONGODB_URI` from `MONGO_ROOT_USERNAME` and `MONGO_ROOT_PASSWORD`. It ignores the `MONGODB_URI` value in `.env`.

## Authentication

The `API_KEY` setting controls authentication.

- If `API_KEY` contains one or more keys, all protected endpoints need the `X-API-Key` header. The header value must be equal to one of the keys.
- If `API_KEY` is empty or not set, authentication is **off**. All endpoints are open.
- The values `none`, `null`, `false` and `disabled` also turn authentication off.

Example with two keys:

```dotenv
API_KEY="key-for-client-a,key-for-client-b"
```

At startup, the server logs a warning if authentication is off.

> [!WARNING]
> Do not run the server without an API key on a network that other people can reach. Clients download and run actuator code from the server. See [Security](security.md).

## Docker

The [`Dockerfile`](../Dockerfile) installs the packages from `requirements.txt`. It runs Gunicorn with 4 Uvicorn workers on port 8000, with a 60 second timeout.

The `mongo` service uses the `mongo:7` image and stores its data in the `nexgen_mongo_data` volume. The `api` service starts after the `mongo` health check passes.

```bash
docker compose up --build      # start the API and MongoDB
docker compose down            # stop the services, keep the data
docker compose down -v         # stop the services and delete the data volume
```

## Logging

The server writes logs to stdout and to a rotating `app.log` file in the working directory. The log file rotates at 100 MB, and the server keeps 5 old files.

Each log line has this format:

```text
<time> | <level> | <logger> | <message>
```

For each request, the message has this format:

```text
<METHOD> <path> -> <status> (<duration>ms) [<request-id>]
```

To trace a request, send an `X-Request-ID` header. The server returns the same value in the response.

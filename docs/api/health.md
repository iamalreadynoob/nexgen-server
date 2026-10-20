# Health API

The health endpoints are public. They do not need the `X-API-Key` header.

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Liveness probe. It checks that the process responds. |
| `GET` | `/api/v1/health/ready` | Readiness probe. It checks that MongoDB is reachable. |

## Liveness

```http
GET /api/v1/health
```

Response `200 OK`:

```json
{"status": "ok"}
```

## Readiness

```http
GET /api/v1/health/ready
```

The server sends a `ping` command to MongoDB.

Response `200 OK`:

```json
{"status": "ready"}
```

If MongoDB is not reachable, the request fails with a server error.

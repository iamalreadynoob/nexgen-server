# Actuators API

An actuator is a versioned, named Python method. Its `actuator_type` is `coding` or `decoding`. See [Concepts](../concepts.md#actuators).

All endpoints need the `X-API-Key` header when `API_KEY` is set. See the [API overview](overview.md) for pagination and errors.

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/actuators` | List the actuators. |
| `GET` | `/api/v1/actuators/{actuator_id}` | Get one actuator by its ID. |
| `GET` | `/api/v1/actuators/{actuator_name}/latest` | Get the latest version of an actuator. |
| `POST` | `/api/v1/actuators` | Create an actuator. |
| `PUT` | `/api/v1/actuators/{actuator_id}` | Mark an actuator as the latest version of its name. |
| `DELETE` | `/api/v1/actuators/{actuator_id}` | Delete an actuator. |

## Actuator object

| Field | Type | Description |
|---|---|---|
| `_id` | string | The ID of the actuator |
| `name` | string | The name of the actuator. 1 to 64 characters. |
| `version` | string | The version of the actuator. 1 to 128 characters. |
| `actuator_type` | string | `coding` or `decoding` |
| `requirements` | array of strings | The Python packages that the method needs, for example `["numpy", "torch"]` |
| `method` | string | The source code of the method |
| `method_args` | object or null | Information about the method arguments, as `{arg_name: {key: value}}` |
| `latest` | boolean | `true` if this is the latest active version of the name |
| `created_at` | string | The creation time (UTC) |
| `updated_at` | string | The time of the last update (UTC) |

Example:

```json
{
  "_id": "6650c0ffee0000000000abcd",
  "name": "text-embedder",
  "version": "1.0.0",
  "actuator_type": "coding",
  "requirements": ["numpy"],
  "method": "def encode(text: str) -> list[float]:\n    ...",
  "method_args": {"text": {"type": "str", "description": "The input sentence"}},
  "latest": true,
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z"
}
```

## List actuators

```http
GET /api/v1/actuators
```

Query parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | integer | `1` | The page number |
| `limit` | integer | `10` | The number of items on each page |
| `ascending` | boolean | `false` | If `true`, the oldest items come first. |
| `latest` | boolean | not set | If `true`, get only the latest versions. If `false`, get only the versions that are not the latest. |

Response `200 OK`:

```json
{
  "total": 1,
  "actuators": [ { "_id": "6650c0ffee0000000000abcd", "name": "text-embedder", "...": "..." } ]
}
```

## Get an actuator

```http
GET /api/v1/actuators/{actuator_id}
```

Response `200 OK`: the actuator object.

Errors:

- `404 Not Found`: No active actuator has the ID.

## Get the latest version

```http
GET /api/v1/actuators/{actuator_name}/latest
```

Use this endpoint to find the version that the transmitter and the receiver must use.

Response `200 OK`: the actuator object.

Errors:

- `404 Not Found`: No active actuator with the name has `latest: true`.

## Create an actuator

```http
POST /api/v1/actuators
```

Request body:

| Field | Type | Necessary | Description |
|---|---|---|---|
| `name` | string | yes | 1 to 64 characters |
| `version` | string | yes | 1 to 128 characters |
| `actuator_type` | string | yes | `coding` or `decoding` |
| `requirements` | array of strings | yes | Use `[]` if the method needs no packages. |
| `method` | string | yes | The source code of the method |
| `method_args` | object | no | Information about the method arguments |
| `set_latest` | boolean | no | If `true`, the new actuator becomes the latest version. The default is `false`. |

Rules:

1. If an active actuator has the same `name` and `version`, the server returns `400 Bad Request`.
2. If no active actuator has the `name`, the new actuator becomes the latest version. This rule applies also when `set_latest` is `false`.
3. If `set_latest` is `true`, the previous latest version loses its latest flag.

Example:

```bash
curl -X POST http://localhost:8000/api/v1/actuators \
  -H "X-API-Key: <your-key>" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "text-embedder",
        "version": "1.1.0",
        "actuator_type": "coding",
        "requirements": ["numpy"],
        "method": "def encode(text: str) -> list[float]:\n    ...",
        "set_latest": true
      }'
```

Response `201 Created`: the actuator object.

Errors:

- `400 Bad Request`: The name and version pair exists already.
- `422 Unprocessable Entity`: The body is not valid.

## Mark an actuator as the latest version

```http
PUT /api/v1/actuators/{actuator_id}
```

The request has no body. The actuator becomes the latest version of its name. The previous latest version loses its latest flag.

Use this endpoint to promote a new version or to roll back to an old version.

Response `200 OK`: the actuator object, with `latest: true`.

Errors:

- `400 Bad Request`: The actuator is the latest version already.
- `404 Not Found`: No active actuator has the ID.

## Delete an actuator

```http
DELETE /api/v1/actuators/{actuator_id}
```

The server sets `active: false` on the actuator. See [Soft delete](overview.md#soft-delete).

You cannot delete the latest version. To delete it, do these steps:

1. Mark a different version as the latest version with `PUT /api/v1/actuators/{other_id}`.
2. Delete the old version.

Response `204 No Content`.

Errors:

- `404 Not Found`: No active actuator has the ID.
- `409 Conflict`: The actuator is the latest version.

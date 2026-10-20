# API Overview

This document gives the rules that apply to all endpoints. The resource documents give each endpoint:

- [Actuators](actuators.md)
- [Data](data.md)
- [Contents](contents.md)
- [Health](health.md)

When `ENVIRONMENT` is not `production`, the server also shows interactive documentation at `/docs`.

## Base URL

All endpoints are under `/api/v1`.

```text
http://<host>:8000/api/v1
```

## Authentication

Send the API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: <your-key>" http://localhost:8000/api/v1/actuators
```

- All endpoints except health need the header when `API_KEY` is set.
- If the key is missing or wrong, the server returns `401 Unauthorized`.
- If `API_KEY` is not set, the server does not check the header.

See [Configuration](../configuration.md#authentication).

## Request ID

You can send an `X-Request-ID` header with each request. The server returns the same value in the `X-Request-ID` response header. If you do not send it, the server makes a new UUID. The server writes the request ID in each request log line.

## Pagination

The list endpoints use these query parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | integer | `1` | The page number. The first page is 1. |
| `limit` | integer | `10` | The number of items on each page |
| `ascending` | boolean | `false` | If `true`, the oldest items come first. If `false`, the newest items come first. |

The server sorts the items by `_id`, which follows the creation order.

Each list response contains `total`, the count of all matching items, and the items on the requested page.

## IDs

All IDs are MongoDB ObjectIds, sent as 24-character hexadecimal strings.

| Resource | ID key in responses |
|---|---|
| Actuator | `_id` |
| Data | `id` |
| Content | `id` |

If an ID is not a valid ObjectId, the server returns `404 Not Found`.

## Soft delete

A `DELETE` request sets `active: false` on the item. After that, the item does not appear in any response. The server does not return the `active` field.

## Timestamps

Each item has `created_at` and `updated_at`. They are UTC times in ISO 8601 format.

## Error responses

The server returns errors as JSON with a `detail` key:

```json
{"detail": "Actuator '6650c0ffee0000000000abcd' not found"}
```

| Status | Cause |
|---|---|
| `400 Bad Request` | The item exists already. Examples: an actuator with the same name and version, or an actuator that is already the latest. |
| `401 Unauthorized` | The API key is missing or wrong. |
| `404 Not Found` | No active item has the ID or the name. The ID is not valid. Or the actuator of a new data item is not the latest version. |
| `409 Conflict` | The request tries to delete the latest version of an actuator. |
| `422 Unprocessable Entity` | The request body or a query parameter is not valid. For a validation error, `detail` is a list of the fields that failed. |

# Contents API

A content item stores the original version of the data. See [Concepts](../concepts.md#contents).

All endpoints need the `X-API-Key` header when `API_KEY` is set. See the [API overview](overview.md) for pagination and errors.

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/contents` | List the content items. You can filter them by specs. |
| `GET` | `/api/v1/contents/{content_id}` | Get one content item. |
| `POST` | `/api/v1/contents` | Create a content item. |
| `PUT` | `/api/v1/contents/{content_id}/specs` | Add or change specs keys of a content item. |
| `DELETE` | `/api/v1/contents/{content_id}` | Delete a content item. |

## Content object

| Field | Type | Description |
|---|---|---|
| `id` | string | The ID of the content item |
| `identifier` | string | The identifier of the original input. Data items can refer to it through `linked_resource`. |
| `specs` | object or null | Free-form information about the content, for example the modality, the format or a storage location |
| `created_at` | string | The creation time (UTC) |
| `updated_at` | string | The time of the last update (UTC) |

Example:

```json
{
  "id": "6650c0ffee0000000000c001",
  "identifier": "sentence-0001",
  "specs": {"modality": "text", "language": "en", "text": "The weather is clear today."},
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z"
}
```

## List content items

```http
GET /api/v1/contents
```

Query parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | integer | `1` | The page number |
| `limit` | integer | `10` | The number of items on each page |
| `ascending` | boolean | `false` | If `true`, the oldest items come first. |
| `specs` | JSON object as a string | not set | A filter on the specs. Each key must be equal to its value. |

Example of a filter for the items with `modality` equal to `text`:

```bash
curl -G http://localhost:8000/api/v1/contents \
  -H "X-API-Key: <your-key>" \
  --data-urlencode 'specs={"modality": "text"}'
```

Response `200 OK`:

```json
{
  "total": 1,
  "data": [ { "id": "6650c0ffee0000000000c001", "identifier": "sentence-0001", "...": "..." } ]
}
```

Errors:

- `422 Unprocessable Entity`: `specs` is not a valid JSON object.

## Get a content item

```http
GET /api/v1/contents/{content_id}
```

Response `200 OK`: the content object.

Errors:

- `404 Not Found`: No active content item has the ID.

## Create a content item

```http
POST /api/v1/contents
```

Request body:

| Field | Type | Necessary | Description |
|---|---|---|---|
| `identifier` | string | yes | The identifier of the original input |
| `specs` | object or null | yes | Free-form information. Send `null` if there is none. |

The server does not check that `identifier` is unique.

Example:

```bash
curl -X POST http://localhost:8000/api/v1/contents \
  -H "X-API-Key: <your-key>" \
  -H "Content-Type: application/json" \
  -d '{
        "identifier": "sentence-0001",
        "specs": {"modality": "text", "text": "The weather is clear today."}
      }'
```

Response `201 Created`: the content object.

Errors:

- `422 Unprocessable Entity`: The body is not valid.

## Add or change specs

```http
PUT /api/v1/contents/{content_id}/specs
```

Request body:

| Field | Type | Necessary | Description |
|---|---|---|---|
| `specs` | object | yes | The keys and values to add or change |

The server merges the given keys into the stored specs:

- A key that exists gets the new value.
- The server adds a new key.
- The other keys do not change.

This is different from `PUT /api/v1/data/{data_id}`, which replaces the full `specs` object.

Example: the stored specs are `{"modality": "text", "language": "en"}`. The request body is `{"specs": {"language": "tr", "split": "test"}}`. The result is `{"modality": "text", "language": "tr", "split": "test"}`.

Response `200 OK`: the content object.

Errors:

- `404 Not Found`: No active content item has the ID.
- `422 Unprocessable Entity`: The body is not valid.

## Delete a content item

```http
DELETE /api/v1/contents/{content_id}
```

The server sets `active: false` on the content item. See [Soft delete](overview.md#soft-delete). The server does not change the data items that refer to the content.

Response `204 No Content`.

Errors:

- `404 Not Found`: No active content item has the ID.

# Data API

A data item stores the output of an actuator, as the link carries or uses it. See [Concepts](../concepts.md#data).

All endpoints need the `X-API-Key` header when `API_KEY` is set. See the [API overview](overview.md) for pagination and errors.

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/data` | List the data items. |
| `GET` | `/api/v1/data/{data_id}` | Get one data item. |
| `POST` | `/api/v1/data` | Create a data item. |
| `PUT` | `/api/v1/data/{data_id}` | Change the linked resource and the specs of a data item. |
| `DELETE` | `/api/v1/data/{data_id}` | Delete a data item. |

## Data object

| Field | Type | Description |
|---|---|---|
| `id` | string | The ID of the data item |
| `actuator_id` | string | The ID of the actuator that made the output |
| `metadata` | any JSON value | The output of the actuator |
| `linked_resource` | string or null | A reference to the original input, for example a content `identifier`. The server does not check this value. |
| `specs` | object or null | Free-form information about the data item |
| `created_at` | string | The creation time (UTC) |
| `updated_at` | string | The time of the last update (UTC) |

Example:

```json
{
  "id": "6650c0ffee0000000000d001",
  "actuator_id": "6650c0ffee0000000000abcd",
  "metadata": [0.12, -0.53, 0.98, 0.07],
  "linked_resource": "sentence-0001",
  "specs": {"modality": "text", "channel": "AWGN", "snr_db": 10},
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z"
}
```

## List data items

```http
GET /api/v1/data
```

Query parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | integer | `1` | The page number |
| `limit` | integer | `10` | The number of items on each page |
| `ascending` | boolean | `false` | If `true`, the oldest items come first. |
| `actuator_id` | string | not set | If set, get only the items that this actuator made. |

Response `200 OK`:

```json
{
  "total": 1,
  "data": [ { "id": "6650c0ffee0000000000d001", "actuator_id": "6650c0ffee0000000000abcd", "...": "..." } ]
}
```

## Get a data item

```http
GET /api/v1/data/{data_id}
```

Query parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `metadata_only` | boolean | `false` | If `true`, the response contains only `id`, `actuator_id` and `metadata`. |

Use `metadata_only=true` when the receiver needs only the actuator output.

Response `200 OK`: the data object. With `metadata_only=true`:

```json
{
  "id": "6650c0ffee0000000000d001",
  "actuator_id": "6650c0ffee0000000000abcd",
  "metadata": [0.12, -0.53, 0.98, 0.07]
}
```

Errors:

- `404 Not Found`: No active data item has the ID.

## Create a data item

```http
POST /api/v1/data
```

Request body:

| Field | Type | Necessary | Description |
|---|---|---|---|
| `actuator_id` | string | yes | The ID of the actuator that made the output |
| `metadata` | any JSON value | yes | The output of the actuator |
| `linked_resource` | string or null | yes | A reference to the original input. Send `null` if there is none. |
| `specs` | object or null | yes | Free-form information. Send `null` if there is none. |

The `actuator_id` must be the **latest** active version of an actuator. The server rejects data from an old version. This rule makes sure that the stored data matches the actuator that the receiver gets.

Example:

```bash
curl -X POST http://localhost:8000/api/v1/data \
  -H "X-API-Key: <your-key>" \
  -H "Content-Type: application/json" \
  -d '{
        "actuator_id": "6650c0ffee0000000000abcd",
        "metadata": [0.12, -0.53, 0.98, 0.07],
        "linked_resource": "sentence-0001",
        "specs": {"modality": "text"}
      }'
```

Response `201 Created`: the data object.

Errors:

- `404 Not Found`: The actuator does not exist, or it is not the latest version.
- `422 Unprocessable Entity`: The body is not valid.

## Change a data item

```http
PUT /api/v1/data/{data_id}
```

Request body:

| Field | Type | Necessary | Description |
|---|---|---|---|
| `linked_resource` | string or null | no | The new linked resource |
| `specs` | object or null | no | The new specs |

- A field that is missing or `null` does not change.
- The new `specs` object replaces the full stored `specs` object. The server does not merge the keys.
- You cannot change `actuator_id` or `metadata`. To store a new output, create a new data item.

Response `200 OK`: the data object.

Errors:

- `404 Not Found`: No active data item has the ID.

## Delete a data item

```http
DELETE /api/v1/data/{data_id}
```

The server sets `active: false` on the data item. See [Soft delete](overview.md#soft-delete).

Response `204 No Content`.

Errors:

- `404 Not Found`: No active data item has the ID.

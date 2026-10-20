# Changelog

All notable changes to this project are recorded in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- changelog-skill: last-documented-commit 329c0cf71fd89d3a6f68463d511814ec268529d8 -->

## [Unreleased]

### Added

- Endpoints to list, read, create and delete actuators under `/api/v1/actuators`.
- `GET /api/v1/actuators/{actuator_name}/latest` returns the latest actuator for a name.
- `PUT /api/v1/actuators/{actuator_id}` makes the actuator the latest version for its name.
- `POST /api/v1/actuators` accepts `set_latest` to make the new actuator the latest version.
- `POST /api/v1/actuators` makes the first actuator for a name the latest version.
- `GET /api/v1/actuators` accepts `page`, `limit`, `ascending` and `latest` query parameters.
- `DELETE /api/v1/actuators/{actuator_id}` returns `409` when the actuator is the latest version.
- Endpoints to list, read, create, update and delete data items under `/api/v1/data`.
- `POST /api/v1/data` accepts only data from the latest actuator and returns `404` for other actuators.
- `GET /api/v1/data/{data_id}` accepts `metadata_only` to return only `id`, `actuator_id` and `metadata`.
- `GET /api/v1/data` accepts an `actuator_id` query parameter to filter the list.
- Endpoints to list, read, create and delete contents under `/api/v1/contents`.
- `PUT /api/v1/contents/{content_id}/specs` adds or changes the given `specs` keys of a content item.
- `GET /api/v1/contents` accepts a `specs` query parameter as a JSON object to filter the list.
- `GET /api/v1/health` and `GET /api/v1/health/ready` report the status of the API and of MongoDB.
- The `X-API-Key` header protects all endpoints except the health endpoints.
- The `API_KEY` setting accepts a comma-separated list of keys and turns off authentication when it is empty.
- The `MONGODB_URI`, `MONGODB_DB`, `ENVIRONMENT` and `LOG_LEVEL` settings configure the server.
- Delete operations mark items as inactive and do not remove them from the database.
- Each response has an `X-Request-ID` header, and the server uses the value from the request if it exists.
- Swagger UI is available at `/docs` when `ENVIRONMENT` is not `production`.
- A `Dockerfile` and a `docker-compose.yaml` file run the API with MongoDB 7.
- A `README.md` file and user guides in `docs/` describe the API, the configuration and the concepts.

[unreleased]: https://github.com/iamalreadynoob/nexgen-server/commits/main

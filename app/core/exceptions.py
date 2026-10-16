"""Exceptions.

It contains the custom exceptions for the app.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    """It is raised once the requested item is not found."""

    def __init__(self, resource: str, identifier: str):
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} '{identifier}' not found")


class AlreadyExistsError(Exception):
    """If the item is being tried to create exists then that error raises."""

    def __init__(self, resource: str, identifier: str):
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} '{identifier}' already exists")


class InvalidFormatError(Exception):
    """It is raised once the given value does not have the expected format."""

    def __init__(self, field: str, expected: str):
        self.field = field
        self.expected = expected
        super().__init__(f"{field} must be {expected}")


def register_exception_handlers(app: FastAPI) -> None:
    """# Register Exception Handlers."""

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_: Request, exc: NotFoundError) -> JSONResponse:
        """# Not Found Handler."""
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(NotFoundError)
    async def already_exists_handler(
        _: Request,
        exc: AlreadyExistsError,
    ) -> JSONResponse:
        """# Not Found Handler."""
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(InvalidFormatError)
    async def invalid_format_handler(
        _: Request,
        exc: InvalidFormatError,
    ) -> JSONResponse:
        """# Invalid Format Handler."""
        return JSONResponse(status_code=422, content={"detail": str(exc)})

"""Errores HTTP de la API. No reinterpretan estados del motor."""

from __future__ import annotations

import math
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger("errors")


class APIError(Exception):
    """Error de negocio con código HTTP y código estable de contrato."""

    def __init__(
        self,
        status_code: int,
        error: str,
        message: str,
        details: Any = None,
    ) -> None:
        self.status_code = status_code
        self.error = error
        self.message = message
        self.details = details
        super().__init__(message)


class EngineUnavailableError(Exception):
    """El motor no publica todavía el punto de entrada solicitado."""


class EngineContractError(Exception):
    """La salida del motor no cumple el contrato que la API puede reenviar."""


def error_body(error: str, message: str, details: Any = None) -> dict[str, Any]:
    body: dict[str, Any] = {"error": error, "message": message}
    if details is not None:
        body["details"] = details
    return body


def _malformed_json(exc: RequestValidationError) -> bool:
    for item in exc.errors():
        if item.get("type") in {"json_invalid", "json_decode"}:
            return True
    return False


def _json_safe(value: Any) -> Any:
    """Quita NaN e infinitos para que el cuerpo de error sea JSON estricto."""

    if isinstance(value, float):
        if not math.isfinite(value):
            return "non_finite"
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    return str(value)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def api_error_handler(_request: Request, exc: APIError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body(exc.error, exc.message, exc.details),
        )

    @app.exception_handler(EngineUnavailableError)
    async def engine_unavailable_handler(
        _request: Request, exc: EngineUnavailableError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content=error_body(
                "ENGINE_UNAVAILABLE",
                "El motor analítico no está disponible para esta operación.",
                details={"reason": str(exc) or "entry_point_missing"},
            ),
        )

    @app.exception_handler(EngineContractError)
    async def engine_contract_handler(
        _request: Request, exc: EngineContractError
    ) -> JSONResponse:
        logger.error("engine_contract_violation %s", exc)
        return JSONResponse(
            status_code=500,
            content=error_body(
                "ENGINE_CONTRACT_VIOLATION",
                "La respuesta del motor no puede publicarse sin alterar el contrato.",
                details={"reason": str(exc)},
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        if _malformed_json(exc):
            return JSONResponse(
                status_code=400,
                content=error_body(
                    "BAD_REQUEST",
                    "El cuerpo no es JSON válido.",
                ),
            )
        return JSONResponse(
            status_code=422,
            content=error_body(
                "VALIDATION_ERROR",
                "La solicitud no cumple el esquema.",
                details=jsonable_encoder(_json_safe(exc.errors())),
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_error")
        return JSONResponse(
            status_code=500,
            content=error_body(
                "INTERNAL_ERROR",
                "Error interno del servidor.",
            ),
        )

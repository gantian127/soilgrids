from __future__ import annotations


class SoilGridsError(Exception):
    """Base error for this package."""


class SoilGridsWcsError(SoilGridsError):
    def __init__(
        self,
        message: str,
        *,
        service_exception: str | None = None,
        raw: str | None = None,
        request: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.service_exception = service_exception
        self.raw = raw
        self.request = request or {}

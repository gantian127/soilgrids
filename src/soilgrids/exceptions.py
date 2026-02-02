from __future__ import annotations


class SoilGridsError(Exception):
    """Base error for this package."""


class SoilGridsWcsError(SoilGridsError):
    """Raised when a WCS request to the SoilGrids service fails.

    This error is raised by :meth:`soilgrids.SoilGrids.get_coverage_data` when the
    remote WCS endpoint returns an OGC exception report (e.g., a
    ``ServiceExceptionReport``) or when the underlying WCS request fails.

    Attributes
    ----------
    service_exception
        Extracted human-readable error text from an OGC exception response, when
        available.
    raw
        Raw decoded response body (typically XML) or a fallback error string when
        parsing is not possible.
    request
        A dictionary with the request context (service/coverage ids, CRS, bbox,
        resolution/size, etc.) to help users debug and/or retry with a smaller
        request.
    """

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

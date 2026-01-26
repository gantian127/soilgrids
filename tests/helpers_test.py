from __future__ import annotations

import pytest

from soilgrids.soilgrids import _extract_ogc_service_exception
from soilgrids.soilgrids import _format_wcs_error_message
from soilgrids.soilgrids import _normalize_content_type


@pytest.mark.parametrize(
    ("content_type", "expected"),
    [
        ("", ""),
        ("application/xml", "application/xml"),
        ("Application/JSON", "application/json"),
        (" application/xml ; charset=UTF-8 ", "application/xml"),
        ("text/plain;charset=ascii", "text/plain"),
        ("application/xml; charset=UTF-8; boundary=xyz", "application/xml"),
        (" ; charset=UTF-8", ""),
    ],
)
def test_normalize_content_type(content_type: str, expected: str):
    assert _normalize_content_type(content_type) == expected


def test_extract_ogc_service_exception_service_exception_tag():
    xml_error = """<?xml version='1.0' encoding="UTF-8" ?>
<ServiceExceptionReport xmlns="http://www.opengis.net/ogc">
  <ServiceException>
    msImageCreate(): Image handling error.
    <Detail>Attempt to allocate raw image failed, out of memory.</Detail>
  </ServiceException>
</ServiceExceptionReport>
"""
    assert _extract_ogc_service_exception(xml_error) == (
        "msImageCreate(): Image handling error.\n"
        "Attempt to allocate raw image failed, out of memory."
    )


def test_extract_ogc_service_exception_exception_text_tag():
    xml_error = """<?xml version="1.0" encoding="UTF-8"?>
<ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1">
  <ows:Exception>
    <ows:ExceptionText>First line</ows:ExceptionText>
    <ows:ExceptionText>Second line</ows:ExceptionText>
  </ows:Exception>
</ows:ExceptionReport>
"""
    assert _extract_ogc_service_exception(xml_error) == "First line"


def test_extract_ogc_service_exception_falls_back_to_exception_text():
    xml_error = """<?xml version="1.0" encoding="UTF-8"?>
<root>
  <ServiceException>   </ServiceException>
  <ExceptionText>Fallback message</ExceptionText>
</root>
"""
    assert _extract_ogc_service_exception(xml_error) == "Fallback message"


@pytest.mark.parametrize(
    "xml_text",
    [
        "not xml",
        "<a><b></a>",
        "<root><ServiceException>   </ServiceException></root>",
    ],
)
def test_extract_ogc_service_exception_returns_none(xml_text: str):
    assert _extract_ogc_service_exception(xml_text) is None


def test_format_wcs_error_message_uses_width_height():
    request_context = {
        "bbox": (-1784000, 1356000, -1140000, 1863000),
        "resx": 250,
        "resy": 250,
        "width": 316,
        "height": 275,
    }
    msg = _format_wcs_error_message("  out of memory  ", request_context)
    assert "WCS server error. out of memory" in msg
    assert "Estimated request size: 316x275 pixels" in msg
    assert "(0.09M pixels)." in msg
    assert "Try reducing the bounding box" in msg
    assert f"Request: {request_context!r}" in msg


def test_format_wcs_error_message_omits_hint_for_non_size_errors():
    request_context = {"width": 100, "height": 100}
    msg = _format_wcs_error_message("Authentication failed", request_context)
    assert "Estimated request size: 100x100 pixels" in msg
    assert "Try reducing the bounding box" not in msg


def test_format_wcs_error_message_estimates_from_bbox_and_resolution():
    request_context = {
        "bbox": (-1784000, 1356000, -1140000, 1863000),
        "resx": 250,
        "resy": 250,
        "width": None,
        "height": None,
    }
    msg = _format_wcs_error_message("WCS failure", request_context)
    assert "Estimated request size: 2576x2028 pixels" in msg
    assert "(5.22M pixels)." in msg


def test_format_wcs_error_message_includes_hint_when_pixel_count_is_large():
    request_context = {"bbox": (0, 0, 1_000_000, 1_000_000), "resx": 1, "resy": 1}
    msg = _format_wcs_error_message("Service error", request_context)
    assert "Estimated request size: 1000000x1000000 pixels" in msg
    assert "Try reducing the bounding box" in msg


@pytest.mark.parametrize(
    "request_context",
    [
        {"bbox": (0, 0, 1, 1), "resx": 0, "resy": 1},
        {"bbox": (0, 0, 1, 1), "resx": -1, "resy": 1},
        {"bbox": (0, 0, 1, 1), "resx": 1, "resy": 0},
        {"bbox": (None, None, None, None), "resx": 1, "resy": 1},
        {"bbox": (0, 0, 10, 10), "resx": 20, "resy": 20},
    ],
)
def test_format_wcs_error_message_omits_pixel_hint_when_uncomputable(
    request_context: dict[str, object],
):
    msg = _format_wcs_error_message("Failure", request_context)
    assert "Estimated request size" not in msg
    assert "Try reducing the bounding box" not in msg


def test_format_wcs_error_message_ignores_partial_width_height_and_uses_bbox():
    request_context = {
        "bbox": (-1784000, 1356000, -1140000, 1863000),
        "resx": 250,
        "resy": 250,
        "width": 316,
        "height": None,
    }
    msg = _format_wcs_error_message("Failure", request_context)
    assert "Estimated request size: 2576x2028 pixels" in msg

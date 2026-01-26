from __future__ import annotations

import os
import xml.etree.ElementTree as ET

import rioxarray
from owslib.util import ServiceException
from owslib.wcs import WebCoverageService
from soilgrids.exceptions import SoilGridsWcsError


class SoilGrids:
    MAP_SERVICES = {
        "bdod": {
            "name": "Bulk density",
            "link": "https://maps.isric.org/mapserv?map=/map/bdod.map",
            "units": "cg/cm3",
        },
        "cec": {
            "name": "Citation exchange capacity at ph7",
            "link": "https://maps.isric.org/mapserv?map=/map/cec.map",
            "units": "mmol(c)/kg",
        },
        "cfvo": {
            "name": "Coarse fragments volumetric",
            "link": "https://maps.isric.org/mapserv?map=/map/cfvo.map",
            "units": "cm3/dm3 (vol‰)",
        },
        "clay": {
            "name": "Clay content",
            "link": "https://maps.isric.org/mapserv?map=/map/clay.map",
            "units": "g/kg",
        },
        "nitrogen": {
            "name": "Nitrogen",
            "link": "https://maps.isric.org/mapserv?map=/map/nitrogen.map",
            "units": "cg/kg",
        },
        "phh2o": {
            "name": "Soil pH in H2O",
            "link": "https://maps.isric.org/mapserv?map=/map/phh2o.map",
            "units": "pH*10",
        },
        "sand": {
            "name": "Sand content",
            "link": "https://maps.isric.org/mapserv?map=/map/sand.map",
            "units": "g/kg",
        },
        "silt": {
            "name": "Silt content",
            "link": "https://maps.isric.org/mapserv?map=/map/silt.map",
            "units": "g/kg",
        },
        "soc": {
            "name": "Soil organic carbon content",
            "link": "https://maps.isric.org/mapserv?map=/map/soc.map",
            "units": "dg/kg",
        },
        "ocs": {
            "name": "Soil organic carbon stock",
            "link": "https://maps.isric.org/mapserv?map=/map/ocs.map",
            "units": "t/ha",
        },
        "ocd": {
            "name": "Organic carbon densities",
            "link": "https://maps.isric.org/mapserv?map=/map/ocd.map",
            "units": "hg/dm3",
        },
        "wrb": {
            "name": "World Reference Base (WRB) classes and probabilities",
            "link": "https://maps.isric.org/mapserv?map=/map/wrb.map",
            "units": "none",
        },
    }
    # service info at http://maps.isric.org/
    # https://www.isric.org/explore/soilgrids/faq-soilgrids

    def __init__(self):
        self._tif_file = None
        self._metadata = None

    @property
    def tif_file(self):
        return self._tif_file

    @property
    def metadata(self):
        return self._metadata

    @property
    def map_services(self):
        string_list = []
        for key, value in SoilGrids.MAP_SERVICES.items():
            string_list.extend(
                [
                    f"service id: {key}",
                    f"variable name: {value['name']}",
                    f"variable units: {value['units']}",
                    f"service link: {value['link']}",
                ]
            )
        print(os.linesep.join(string_list))

    def get_coverage_list(self, service_id):
        _, coverage_list = self._get_service_and_coverage_list(service_id)

        print(
            f"{service_id!r} map service includes {len(coverage_list)} coverages(maps)"
        )
        print(os.linesep.join(coverage_list))

    def get_coverage_info(self, service_id, coverage_id):
        wcs, coverage_list = self._get_service_and_coverage_list(service_id)
        coverage_obj = self._get_coverage_obj(wcs, coverage_list, coverage_id)

        print(
            "Supported CRS: \n{}\n".format(
                "\n".join([CRS.getcodeurn() for CRS in coverage_obj.supportedCRS])
            )
        )
        print(
            "Coverage Bounding Box: \n{}\n".format(
                "\n".join(
                    [
                        "{}\n{}".format(bbox["nativeSrs"], bbox["bbox"])
                        for bbox in coverage_obj.boundingboxes
                    ]
                )
            )
        )

        return None

    def get_coverage_data(
        self,
        service_id,
        coverage_id,
        crs,
        west,
        south,
        east,
        north,
        output,
        resx=250,
        resy=250,
        width=None,
        height=None,
        response_crs=None,
        local_file=False,
    ):
        wcs, coverage_list = self._get_service_and_coverage_list(service_id)
        coverage_obj = self._get_coverage_obj(wcs, coverage_list, coverage_id)

        # check crs
        crs_list = [CRS.getcodeurn() for CRS in coverage_obj.supportedCRS]
        if crs not in crs_list:
            raise ValueError(
                "Please provide a coordinate system code from the following options"
                " for crs:\n"
                f"{os.linesep.join(crs_list)}"
            )
        if "4326" in crs:
            if width and height:
                resx = resy = None
            else:
                raise ValueError(
                    "Please provide width and height values when the coordinate"
                    " system (crs) is EPSG 4326."
                )
        else:
            width = height = None

        # check response_crs
        if response_crs is None:
            response_crs = crs
        elif response_crs not in crs_list:
            raise ValueError(
                "Please provide a coordinate system code from the following options"
                " for response_crs:\n"
                f"{os.linesep.join(crs_list)}"
            )

        # check bounding box
        if west > east or south > north:
            raise ValueError(
                "Please provide valid bounding box values for west, east, south and"
                " north."
            )
        else:
            bbox = (west, south, east, north)

        # check output
        if output[-4::] != ".tif":
            raise ValueError(
                "Please provide a valid output file name with .tif extension."
            )

        if local_file and os.path.isfile(output):
            pass
        else:
            request_context = {
                "service_id": service_id,
                "coverage_id": coverage_id,
                "crs": crs,
                "bbox": bbox,
                "resx": resx,
                "resy": resy,
                "width": width,
                "height": height,
                "response_crs": response_crs,
                "format": "GEOTIFF_INT16",
            }

            try:
                response = wcs.getCoverage(
                    identifier=coverage_id,
                    crs=crs,
                    bbox=bbox,
                    resx=resx,
                    resy=resy,
                    width=width,
                    height=height,
                    response_crs=response_crs,
                    format="GEOTIFF_INT16",
                )
            except ServiceException as exc:
                raise SoilGridsWcsError(
                    _format_wcs_error_message(str(exc), request_context),
                    service_exception=str(exc),
                    raw=str(exc),
                    request=request_context,
                ) from exc
            except Exception as exc:
                raise SoilGridsWcsError(
                    _format_wcs_error_message(str(exc), request_context),
                    raw=str(exc),
                    request=request_context,
                ) from exc

            content_type = _normalize_content_type(
                response.info().get("Content-Type", "")
            )
            body = response.read()

            if "tiff" in content_type:
                try:
                    with open(output, "wb") as file:
                        file.write(body)
                except Exception as exc:
                    raise SoilGridsWcsError(
                        _format_wcs_error_message(
                            f"Failed to save the data as a GeoTiff file to {output!r}: {exc}",
                            request_context,
                        ),
                        raw=str(exc),
                        request=request_context,
                    ) from exc
            else:
                raw = body.decode("utf-8", errors="replace")
                service_exception = _extract_ogc_service_exception(raw)
                details = service_exception or raw
                raise SoilGridsWcsError(
                    _format_wcs_error_message(details, request_context),
                    service_exception=service_exception,
                    raw=raw,
                    request=request_context,
                )

        # open data
        dataset = rioxarray.open_rasterio(output)
        dataset.close()

        # get resolution
        if resx and resy:
            grid_res = [resx, resy]
        else:
            geotrans = [
                float(value)
                for value in dataset["spatial_ref"].attrs["GeoTransform"].split(" ")
            ]
            grid_res = [abs(geotrans[1]), abs(geotrans[5])]

        # store metadata
        self._tif_file = (
            output
            if os.path.dirname(output) != ""
            else os.path.join(os.getcwd(), output)
        )
        self._metadata = {
            "variable_name": SoilGrids.MAP_SERVICES[service_id]["name"],
            "variable_units": SoilGrids.MAP_SERVICES[service_id]["units"],
            "service_url": SoilGrids.MAP_SERVICES[service_id]["link"],
            "service_id": service_id,
            "coverage_id": coverage_id,
            "crs": response_crs,
            "bounding_box": bbox,
            "grid_res": grid_res,
        }

        return dataset

    @staticmethod
    def _get_service_and_coverage_list(service_id):
        if service_id not in SoilGrids.MAP_SERVICES.keys():
            raise ValueError(
                "Please provide a service id from the following options: \n{}".format(
                    "\n".join(
                        [
                            "{}: {}".format(key, value["name"])
                            for key, value in SoilGrids.MAP_SERVICES.items()
                        ]
                    )
                )
            )
        else:
            service_link = SoilGrids.MAP_SERVICES[service_id]["link"]
            wcs = WebCoverageService(service_link, version="1.0.0")
            coverage_list = list(wcs.contents)

        return wcs, coverage_list

    @staticmethod
    def _get_coverage_obj(wcs, coverage_list, coverage_id):
        if coverage_id not in coverage_list:
            raise ValueError(
                "Please provide a coverage id from the following options: \n{}".format(
                    "\n".join(coverage_list)
                )
            )
        else:
            coverage_obj = wcs.contents[coverage_id]

        return coverage_obj


def _normalize_content_type(content_type: str) -> str:
    return content_type.split(";", 1)[0].strip().lower() if content_type else ""


def _extract_ogc_service_exception(xml_text: str) -> str | None:
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return None

    for tag_suffix in ("ServiceException", "ExceptionText"):
        for elem in root.iter():
            if isinstance(elem.tag, str) and elem.tag.endswith(tag_suffix):
                message = "\n".join(
                    t.strip()
                    for t in elem.itertext()
                    if isinstance(t, str) and t.strip()
                )
                if message:
                    return message
    return None


def _format_wcs_error_message(details: str, request_context: dict[str, object]) -> str:
    west, south, east, north = request_context.get("bbox", (None, None, None, None))
    resx = request_context.get("resx")
    resy = request_context.get("resy")
    width = request_context.get("width")
    height = request_context.get("height")

    est_width = None
    est_height = None
    if isinstance(width, (int, float)) and isinstance(height, (int, float)):
        est_width = int(width)
        est_height = int(height)
    elif (
        isinstance(west, (int, float))
        and isinstance(east, (int, float))
        and isinstance(south, (int, float))
        and isinstance(north, (int, float))
        and isinstance(resx, (int, float))
        and isinstance(resy, (int, float))
        and resx > 0
        and resy > 0
    ):
        est_width = int(abs(east - west) / resx)
        est_height = int(abs(north - south) / resy)

    pixel_hint = ""
    pixels = None
    if est_width and est_height:
        pixels = est_width * est_height
        pixels_m = pixels / 1_000_000
        pixel_hint = (
            f" Estimated request size: {est_width}x{est_height} pixels"
            f" ({pixels_m:.2f}M pixels)."
        )

    details_lower = details.lower() if details else ""
    size_error_keywords = (
        "memory",
        "out of memory",
        "too large",
        "too big",
        "size",
        "exceed",
        "exceeded",
        "limit",
        "maximum",
    )
    size_hint_pixel_threshold = 50_000_000
    include_hint = any(k in details_lower for k in size_error_keywords) or (
        isinstance(pixels, int) and pixels >= size_hint_pixel_threshold
    )
    hint = (
        " Try reducing the bounding box, increasing resx/resy, or tiling the request."
        if include_hint
        else ""
    )

    return (
        "WCS server error. "
        f"{details.strip()}"
        f"{pixel_hint}"
        f"{hint}"
        f" Request: {request_context!r}"
    )

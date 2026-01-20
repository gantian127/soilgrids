from __future__ import annotations

import os

import pytest
import xarray
from soilgrids import SoilGrids


# test get_coverage_list()
def test_get_coverage_list():
    with pytest.raises(ValueError):
        SoilGrids().get_coverage_list("wrong_service_id")


# test get_coverage_info()
def test_get_coverage_info():
    with pytest.raises(ValueError):
        SoilGrids().get_coverage_info("wrong_service_id", "wrong_coverage_id")

    with pytest.raises(ValueError):
        SoilGrids().get_coverage_info("bdod", "wrong_coverage_id")


# test user input for get_coverage_data()
def test_service_id():
    with pytest.raises(ValueError):
        SoilGrids().get_coverage_data(
            "wrong id",
            "phh2o_0-5cm_mean",
            crs="urn:ogc:def:crs:EPSG::152160",
            west=-1784000,
            south=1356000,
            east=-1140000,
            north=1863000,
            output="test.tif",
        )


def test_coverage_id():
    with pytest.raises(ValueError):
        SoilGrids().get_coverage_data(
            "phh2o",
            "wrong id",
            crs="urn:ogc:def:crs:EPSG::152160",
            west=-1784000,
            south=1356000,
            east=-1140000,
            north=1863000,
            output="test.tif",
        )


def test_crs():
    with pytest.raises(ValueError):
        SoilGrids().get_coverage_data(
            "phh2o",
            "phh2o_0-5cm_mean",
            crs="wrong code",
            west=-1784000,
            south=1356000,
            east=-1140000,
            north=1863000,
            output="test.tif",
        )


def test_bounding_box():
    with pytest.raises(ValueError):  # west > east
        SoilGrids().get_coverage_data(
            "phh2o",
            "phh2o_0-5cm_mean",
            crs="urn:ogc:def:crs:EPSG::152160",
            west=1784000,
            south=1356000,
            east=-1140000,
            north=1863000,
            output="test.tif",
        )

    with pytest.raises(ValueError):  # south>north
        SoilGrids().get_coverage_data(
            "phh2o",
            "phh2o_0-5cm_mean",
            crs="urn:ogc:def:crs:EPSG::152160",
            west=-1784000,
            south=1356000,
            east=-1140000,
            north=-1863000,
            output="test.tif",
        )


def test_output():
    with pytest.raises(ValueError):
        SoilGrids().get_coverage_data(
            "phh2o",
            "phh2o_0-5cm_mean",
            crs="urn:ogc:def:crs:EPSG::152160",
            west=-1784000,
            south=1356000,
            east=-1140000,
            north=1863000,
            output="wrong file",
        )


def test_width_height():
    with pytest.raises(ValueError):
        SoilGrids().get_coverage_data(
            "phh2o",
            "phh2o_0-5cm_mean",
            crs="urn:ogc:def:crs:EPSG::4326",
            west=-105.38,
            south=39.45,
            east=-104.5,
            north=40.07,
            output="test.tif",
        )


def test_response_crs():
    with pytest.raises(ValueError):
        SoilGrids().get_coverage_data(
            "phh2o",
            "phh2o_0-5cm_mean",
            crs="urn:ogc:def:crs:EPSG::4326",
            west=-1784000,
            south=1356000,
            east=-1140000,
            north=1863000,
            response_crs="error",
            output="test.tif",
        )


def test_wcs_service_exception_report_is_raised(tmp_path, monkeypatch):
    xml_error = """<?xml version='1.0' encoding="UTF-8" ?>
<ServiceExceptionReport version="1.2.0"
xmlns="http://www.opengis.net/ogc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/ogc http://schemas.opengis.net/wcs/1.0.0/OGC-exception.xsd">
  <ServiceException>msImageCreate(): Image handling error. Attempt to allocate raw image failed, out of memory.
  </ServiceException>
</ServiceExceptionReport>
"""

    class DummyCRS:
        def __init__(self, code):
            self._code = code

        def getcodeurn(self):
            return self._code

    class DummyCoverage:
        supportedCRS = [DummyCRS("urn:ogc:def:crs:EPSG::152160")]

    class DummyResponse:
        def info(self):
            return {"Content-Type": "application/xml"}

        def read(self):
            return xml_error.encode("utf-8")

    class DummyWCS:
        def getCoverage(self, **_kwargs):
            return DummyResponse()

    soilgrids = SoilGrids()
    monkeypatch.setattr(
        soilgrids,
        "_get_service_and_coverage_list",
        lambda _service_id: (DummyWCS(), ["phh2o_0-5cm_mean"]),
    )
    monkeypatch.setattr(soilgrids, "_get_coverage_obj", lambda *_args: DummyCoverage())

    output = tmp_path / "test.tif"
    with pytest.raises(Exception) as excinfo:
        soilgrids.get_coverage_data(
            "phh2o",
            "phh2o_0-5cm_mean",
            crs="urn:ogc:def:crs:EPSG::152160",
            west=-1784000,
            south=1356000,
            east=-1140000,
            north=1863000,
            output=str(output),
        )

    assert "WCS sever error" in str(excinfo.value)
    assert "out of memory" in str(excinfo.value)
    assert not output.exists()


# test data download for get_coverage_data()
@pytest.mark.filterwarnings("ignore:numpy.ufunc size")
def test_data_download(tmpdir):
    data = SoilGrids().get_coverage_data(
        "phh2o",
        "phh2o_0-5cm_mean",
        crs="urn:ogc:def:crs:EPSG::152160",
        west=-1784000,
        south=1356000,
        east=-1140000,
        north=1863000,
        output=os.path.join(tmpdir, "test.tif"),
    )

    assert isinstance(data, xarray.core.dataarray.DataArray)
    assert len(os.listdir(tmpdir)) == 1

    data2 = SoilGrids().get_coverage_data(
        "phh2o",
        "phh2o_0-5cm_mean",
        crs="urn:ogc:def:crs:EPSG::4326",
        west=-105.38,
        south=39.45,
        east=-104.5,
        north=40.07,
        width=316,
        height=275,
        output=os.path.join(tmpdir, "test2.tif"),
    )

    assert isinstance(data2, xarray.core.dataarray.DataArray)
    assert len(os.listdir(tmpdir)) == 2

    data3 = SoilGrids().get_coverage_data(
        "phh2o",
        "phh2o_0-5cm_mean",
        crs="urn:ogc:def:crs:EPSG::4326",
        west=-105.38,
        south=39.45,
        east=-104.5,
        north=40.07,
        response_crs="urn:ogc:def:crs:EPSG::152160",
        width=316,
        height=275,
        output=os.path.join(tmpdir, "test3.tif"),
    )

    assert isinstance(data3, xarray.core.dataarray.DataArray)
    assert len(os.listdir(tmpdir)) == 3


# test loading local file for get_coverage_data()
@pytest.mark.filterwarnings("ignore:numpy.ufunc size")
def test_load_localfile(tmpdir):
    SoilGrids().get_coverage_data(
        "phh2o",
        "phh2o_0-5cm_mean",
        crs="urn:ogc:def:crs:EPSG::152160",
        west=-1784000,
        south=1356000,
        east=-1140000,
        north=1863000,
        output=os.path.join(tmpdir, "test.tif"),
    )
    file1_info = os.path.getmtime(os.path.join(tmpdir, "test.tif"))
    assert len(os.listdir(tmpdir)) == 1

    SoilGrids().get_coverage_data(
        "phh2o",
        "phh2o_0-5cm_mean",
        crs="urn:ogc:def:crs:EPSG::152160",
        west=-1784000,
        south=1356000,
        east=-1140000,
        north=1863000,
        output=os.path.join(tmpdir, "test.tif"),
        local_file=True,
    )
    file2_info = os.path.getmtime(os.path.join(tmpdir, "test.tif"))

    assert file1_info == file2_info

import pytest
import os

import xarray

from soilgrids import SoilGrids


# test get_coverage_list()
def test_get_coverage_list():
    with pytest.raises(ValueError):
        SoilGrids().get_coverage_list('wrong_service_id')


# test get_coverage_info()
def test_get_coverage_info():
    with pytest.raises(ValueError):
        SoilGrids().get_coverage_info('wrong_service_id', 'wrong_coverage_id')

    with pytest.raises(ValueError):
        SoilGrids().get_coverage_info('bdod', 'wrong_coverage_id')


# test user input for get_coverage_data()
def test_service_id():
    with pytest.raises(ValueError):
        SoilGrids().get_coverage_data('wrong id', 'phh2o_0-5cm_mean', crs='urn:ogc:def:crs:EPSG::152160',
                                      west=-1784000, south=1356000, east=-1140000, north=1863000, output='test.tif')


def test_coverage_id():
    with pytest.raises(ValueError):
        SoilGrids().get_coverage_data('phh2o', 'wrong id', crs='urn:ogc:def:crs:EPSG::152160',
                                      west=-1784000, south=1356000, east=-1140000, north=1863000, output='test.tif')


def test_crs():
    with pytest.raises(ValueError):
        SoilGrids().get_coverage_data('phh2o', 'phh2o_0-5cm_mean', crs='wrong code',
                                      west=-1784000, south=1356000, east=-1140000, north=1863000, output='test.tif')


def test_bounding_box():
    with pytest.raises(ValueError):  # west > east
        SoilGrids().get_coverage_data('phh2o', 'phh2o_0-5cm_mean', crs='urn:ogc:def:crs:EPSG::152160',
                                      west=1784000, south=1356000, east=-1140000, north=1863000, output='test.tif')

    with pytest.raises(ValueError):  # south>north
        SoilGrids().get_coverage_data('phh2o', 'phh2o_0-5cm_mean', crs='urn:ogc:def:crs:EPSG::152160',
                                      west=-1784000, south=1356000, east=-1140000, north=-1863000, output='test.tif')


def test_output():
    with pytest.raises(ValueError):
        SoilGrids().get_coverage_data('phh2o', 'phh2o_0-5cm_mean', crs='urn:ogc:def:crs:EPSG::152160',
                                      west=-1784000, south=1356000, east=-1140000, north=1863000, output='wrong file')


def test_width_height():
    with pytest.raises(ValueError):
        SoilGrids().get_coverage_data('phh2o', 'phh2o_0-5cm_mean', crs='urn:ogc:def:crs:EPSG::4326',
                                      west=-105.38, south=39.45, east=-104.5, north=40.07, output='test.tif')


def test_response_crs():
    with pytest.raises(ValueError):
        SoilGrids().get_coverage_data('phh2o', 'phh2o_0-5cm_mean', crs='urn:ogc:def:crs:EPSG::4326',
                                      west=-1784000, south=1356000, east=-1140000, north=1863000,
                                      response_crs='error', output='test.tif')


# test data download for get_coverage_data()
@pytest.mark.filterwarnings("ignore:numpy.ufunc size")
def test_data_download(tmpdir):
    data = SoilGrids().get_coverage_data('phh2o', 'phh2o_0-5cm_mean', crs='urn:ogc:def:crs:EPSG::152160',
                                         west=-1784000, south=1356000, east=-1140000, north=1863000,
                                         output=os.path.join(tmpdir, 'test.tif'))

    assert isinstance(data, xarray.core.dataarray.DataArray)
    assert len(os.listdir(tmpdir)) == 1

    data2 = SoilGrids().get_coverage_data('phh2o', 'phh2o_0-5cm_mean', crs='urn:ogc:def:crs:EPSG::4326',
                                          west=-105.38, south=39.45, east=-104.5, north=40.07,
                                          width=316, height=275, output=os.path.join(tmpdir, 'test2.tif'))

    assert isinstance(data2, xarray.core.dataarray.DataArray)
    assert len(os.listdir(tmpdir)) == 2

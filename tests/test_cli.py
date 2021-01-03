#!/usr/bin/env python
import os

import pytest

from click.testing import CliRunner

from soilgrids.cli import main


def test_command_line_interface():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output

    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output


def test_output(tmpdir):
    runner = CliRunner()

    result = runner.invoke(main, ['--service_id=phh2o', '--coverage_id=phh2o_0-5cm_mean',
                                  '--crs=urn:ogc:def:crs:EPSG::152160',
                                  '--bbox=-1784000,1356000,-1140000,1863000',
                                  'error'])
    assert result.exit_code != 0


def test_service_id():
    runner = CliRunner()
    result = runner.invoke(main, ['--service_id=error', '--coverage_id=phh2o_0-5cm_mean',
                                  '--crs=urn:ogc:def:crs:EPSG::152160',
                                  '--bbox=-1784000,1356000,-1140000,1863000',
                                  'test.tif'])
    assert result.exit_code != 0


def test_coverage_id():
    runner = CliRunner()
    result = runner.invoke(main, ['--service_id=phh2o', '--coverage_id=error',
                                  '--crs=urn:ogc:def:crs:EPSG::152160',
                                  '--bbox=-1784000,1356000,-1140000,1863000',
                                  'test.tif'])
    assert result.exit_code != 0


def test_crs():
    runner = CliRunner()
    result = runner.invoke(main, ['--service_id=phh2o', '--coverage_id=phh2o_0-5cm_mean',
                                  '--crs=error',
                                  '--bbox=-1784000,1356000,-1140000,1863000',
                                  'test.tif'])
    assert result.exit_code != 0


def test_bbox():
    runner = CliRunner()
    result = runner.invoke(main, ['--service_id=phh2o', '--coverage_id=phh2o_0-5cm_mean',
                                  '--crs=urn:ogc:def:crs:EPSG::152160',
                                  '--bbox=1784000,1356000,-1140000,1863000',
                                  'test.tif'])
    assert result.exit_code != 0


def test_width_height():
    runner = CliRunner()
    result = runner.invoke(main, ['--service_id=phh2o', '--coverage_id=phh2o_0-5cm_mean',
                                  '--crs=urn:ogc:def:crs:EPSG::4326',
                                  '--bbox=1784000,1356000,-1140000,1863000',
                                  'test.tif'])

    assert result.exit_code != 0


def test_response_crs():
    runner = CliRunner()
    result = runner.invoke(main, ['--service_id=phh2o', '--coverage_id=phh2o_0-5cm_mean',
                                  '--crs=urn:ogc:def:crs:EPSG::152160',
                                  '--bbox=-1784000,1356000,-1140000,1863000',
                                  '--response_crs=error',
                                  'test.tif'])

    assert result.exit_code != 0


@pytest.mark.filterwarnings("ignore:numpy.ufunc size")
def test_data_download(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        result = runner.invoke(main, ['--service_id=phh2o', '--coverage_id=phh2o_0-5cm_mean',
                                      '--crs=urn:ogc:def:crs:EPSG::152160',
                                      '--bbox=-1784000,1356000,-1140000,1863000',
                                      '--resx=500', '--resy=500',
                                      'test.tif'])

        assert result.exit_code == 0
        assert len(os.listdir(tmpdir)) == 1

    with tmpdir.as_cwd():
        result = runner.invoke(main, ['--service_id=phh2o', '--coverage_id=phh2o_0-5cm_mean',
                                      '--crs=urn:ogc:def:crs:EPSG::4326',
                                      '--bbox=-105.38, 39.45, -104.5, 40.07',
                                      '--width=316', '--height=275',
                                      'test2.tif'])
        assert result.exit_code == 0
        assert len(os.listdir(tmpdir)) == 2

    with tmpdir.as_cwd():
        result = runner.invoke(main, ['--service_id=phh2o', '--coverage_id=phh2o_0-5cm_mean',
                                      '--crs=urn:ogc:def:crs:EPSG::4326',
                                      '--bbox=-105.38, 39.45, -104.5, 40.07',
                                      '--width=316', '--height=275',
                                      '--response_crs=urn:ogc:def:crs:EPSG::152160',
                                      'test3.tif'])
        assert result.exit_code == 0
        assert len(os.listdir(tmpdir)) == 3

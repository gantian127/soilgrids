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

@pytest.mark.filterwarnings("ignore:numpy.ufunc size")
def test_output(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        result = runner.invoke(main, ['--ser_id=phh2o', '--cov_id=phh2o_0-5cm_mean',
                                      '--crs=urn:ogc:def:crs:EPSG::152160',
                                      '--bbox=-1784000,1356000,-1140000,1863000',
                                      'error'])
        assert result.exit_code != 0
        assert len(os.listdir(tmpdir)) == 0

    with tmpdir.as_cwd():
        result = runner.invoke(main, ['--ser_id=phh2o', '--cov_id=phh2o_0-5cm_mean',
                                      '--crs=urn:ogc:def:crs:EPSG::152160',
                                      '--bbox=-1784000,1356000,-1140000,1863000',
                                      'test.tif'])

        assert result.exit_code == 0
        assert len(os.listdir(tmpdir)) == 1


def test_ser_id():
    runner = CliRunner()
    result = runner.invoke(main, ['--ser_id=error', '--cov_id=phh2o_0-5cm_mean',
                                  '--crs=urn:ogc:def:crs:EPSG::152160',
                                  '--bbox=-1784000,1356000,-1140000,1863000',
                                  'test.tif'])
    assert result.exit_code != 0


def test_cov_id():
    runner = CliRunner()
    result = runner.invoke(main, ['--ser_id=phh2o', '--cov_id=error',
                                  '--crs=urn:ogc:def:crs:EPSG::152160',
                                  '--bbox=-1784000,1356000,-1140000,1863000',
                                  'test.tif'])
    assert result.exit_code != 0


def test_crs():
    runner = CliRunner()
    result = runner.invoke(main, ['--ser_id=phh2o', '--cov_id=phh2o_0-5cm_mean',
                                  '--crs=error',
                                  '--bbox=-1784000,1356000,-1140000,1863000',
                                  'test.tif'])
    assert result.exit_code != 0


def test_bbox():
    runner = CliRunner()
    result = runner.invoke(main, ['--ser_id=phh2o', '--cov_id=phh2o_0-5cm_mean',
                                  '--crs=urn:ogc:def:crs:EPSG::152160',
                                  '--bbox=1784000,1356000,-1140000,1863000',
                                  'test.tif'])
    assert result.exit_code != 0

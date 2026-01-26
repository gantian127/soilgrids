#!/usr/bin/env python
from __future__ import annotations

import os

import pytest
import soilgrids.cli as cli_module
from click.testing import CliRunner
from soilgrids import SoilGridsWcsError


def test_command_line_interface():
    runner = CliRunner()
    result = runner.invoke(cli_module.main, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output

    result = runner.invoke(cli_module.main, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output


def test_output(tmpdir):
    runner = CliRunner()

    result = runner.invoke(
        cli_module.main,
        [
            "--service_id=phh2o",
            "--coverage_id=phh2o_0-5cm_mean",
            "--crs=urn:ogc:def:crs:EPSG::152160",
            "--bbox=-1784000,1356000,-1140000,1863000",
            "error",
        ],
    )
    assert result.exit_code != 0


def test_service_id():
    runner = CliRunner()
    result = runner.invoke(
        cli_module.main,
        [
            "--service_id=error",
            "--coverage_id=phh2o_0-5cm_mean",
            "--crs=urn:ogc:def:crs:EPSG::152160",
            "--bbox=-1784000,1356000,-1140000,1863000",
            "test.tif",
        ],
    )
    assert result.exit_code != 0


def test_coverage_id():
    runner = CliRunner()
    result = runner.invoke(
        cli_module.main,
        [
            "--service_id=phh2o",
            "--coverage_id=error",
            "--crs=urn:ogc:def:crs:EPSG::152160",
            "--bbox=-1784000,1356000,-1140000,1863000",
            "test.tif",
        ],
    )
    assert result.exit_code != 0


def test_crs():
    runner = CliRunner()
    result = runner.invoke(
        cli_module.main,
        [
            "--service_id=phh2o",
            "--coverage_id=phh2o_0-5cm_mean",
            "--crs=error",
            "--bbox=-1784000,1356000,-1140000,1863000",
            "test.tif",
        ],
    )
    assert result.exit_code != 0


def test_bbox():
    runner = CliRunner()
    result = runner.invoke(
        cli_module.main,
        [
            "--service_id=phh2o",
            "--coverage_id=phh2o_0-5cm_mean",
            "--crs=urn:ogc:def:crs:EPSG::152160",
            "--bbox=1784000,1356000,-1140000,1863000",
            "test.tif",
        ],
    )
    assert result.exit_code != 0


def test_width_height():
    runner = CliRunner()
    result = runner.invoke(
        cli_module.main,
        [
            "--service_id=phh2o",
            "--coverage_id=phh2o_0-5cm_mean",
            "--crs=urn:ogc:def:crs:EPSG::4326",
            "--bbox=1784000,1356000,-1140000,1863000",
            "test.tif",
        ],
    )

    assert result.exit_code != 0


def test_response_crs():
    runner = CliRunner()
    result = runner.invoke(
        cli_module.main,
        [
            "--service_id=phh2o",
            "--coverage_id=phh2o_0-5cm_mean",
            "--crs=urn:ogc:def:crs:EPSG::152160",
            "--bbox=-1784000,1356000,-1140000,1863000",
            "--local_file=error",
            "test.tif",
        ],
    )

    assert result.exit_code != 0


def test_local_file():
    runner = CliRunner()
    result = runner.invoke(
        cli_module.main,
        [
            "--service_id=phh2o",
            "--coverage_id=phh2o_0-5cm_mean",
            "--crs=urn:ogc:def:crs:EPSG::152160",
            "--bbox=-1784000,1356000,-1140000,1863000",
            "--local_file=error",
            "test.tif",
        ],
    )

    assert result.exit_code != 0


def test_cli_converts_soilgrids_error_to_click_exception(monkeypatch, tmp_path):
    def raise_wcs_error(*_args, **_kwargs):
        raise SoilGridsWcsError("WCS server error. out of memory", request={})

    monkeypatch.setattr(cli_module.SoilGrids, "get_coverage_data", raise_wcs_error)

    runner = CliRunner()
    result = runner.invoke(
        cli_module.main,
        [
            "--service_id=phh2o",
            "--coverage_id=phh2o_0-5cm_mean",
            "--crs=urn:ogc:def:crs:EPSG::152160",
            "--bbox=-1,0,1,2",
            str(tmp_path / "test.tif"),
        ],
    )

    assert result.exit_code != 0
    assert "Error:" in result.output
    assert "out of memory" in result.output
    assert "Traceback" not in result.output


@pytest.mark.filterwarnings("ignore:numpy.ufunc size")
def test_data_download(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        result = runner.invoke(
            cli_module.main,
            [
                "--service_id=phh2o",
                "--coverage_id=phh2o_0-5cm_mean",
                "--crs=urn:ogc:def:crs:EPSG::152160",
                "--bbox=-1784000,1356000,-1140000,1863000",
                "--resx=500",
                "--resy=500",
                "test.tif",
            ],
        )

        assert result.exit_code == 0
        assert len(os.listdir(tmpdir)) == 1

    with tmpdir.as_cwd():
        result = runner.invoke(
            cli_module.main,
            [
                "--service_id=phh2o",
                "--coverage_id=phh2o_0-5cm_mean",
                "--crs=urn:ogc:def:crs:EPSG::4326",
                "--bbox=-105.38, 39.45, -104.5, 40.07",
                "--width=316",
                "--height=275",
                "test2.tif",
            ],
        )
        assert result.exit_code == 0
        assert len(os.listdir(tmpdir)) == 2

    with tmpdir.as_cwd():
        result = runner.invoke(
            cli_module.main,
            [
                "--service_id=phh2o",
                "--coverage_id=phh2o_0-5cm_mean",
                "--crs=urn:ogc:def:crs:EPSG::4326",
                "--bbox=-105.38, 39.45, -104.5, 40.07",
                "--width=316",
                "--height=275",
                "--response_crs=urn:ogc:def:crs:EPSG::152160",
                "test3.tif",
            ],
        )
        assert result.exit_code == 0
        assert len(os.listdir(tmpdir)) == 3


@pytest.mark.filterwarnings("ignore:numpy.ufunc size")
def test_load_localfile(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        result = runner.invoke(
            cli_module.main,
            [
                "--service_id=phh2o",
                "--coverage_id=phh2o_0-5cm_mean",
                "--crs=urn:ogc:def:crs:EPSG::152160",
                "--bbox=-1784000,1356000,-1140000,1863000",
                "--resx=500",
                "--resy=500",
                "test.tif",
            ],
        )

        assert result.exit_code == 0
        assert len(os.listdir(tmpdir)) == 1
        file1_info = os.path.getmtime("test.tif")

    with tmpdir.as_cwd():
        result = runner.invoke(
            cli_module.main,
            [
                "--service_id=phh2o",
                "--coverage_id=phh2o_0-5cm_mean",
                "--crs=urn:ogc:def:crs:EPSG::152160",
                "--bbox=-1784000,1356000,-1140000,1863000",
                "--resx=500",
                "--resy=500",
                "--local_file=True",
                "test.tif",
            ],
        )

        assert result.exit_code == 0
        assert len(os.listdir(tmpdir)) == 1
        file2_info = os.path.getmtime("test.tif")

    assert file1_info == file2_info

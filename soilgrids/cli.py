import os
import click

from . import __version__
from soilgrids import SoilGrids


@click.command()
@click.version_option(version=__version__)
@click.option(
    "--service_id",
    required=True,
    help="Map service identifier for a map service. "
         "See details at https://www.isric.org/explore/soilgrids/faq-soilgrids",
)
@click.option(
    "--coverage_id",
    required=True,
    help="Map coverage identifier supported by a map service.",
)
@click.option(
    "--crs",
    required=True,
    help="Coordinate system code for a map coverage.",
)
@click.option(
    "--bbox",
    required=True,
    help="Bounding box for data download . "
         "Values are based on the specified crs in a sequence of west, south, east, north separated by comma.",
)
@click.argument(
    'output',
    type=click.Path(exists=False)
)
def main(service_id, coverage_id, crs, bbox, output):
    west, south, east, north = list(map(float, bbox.split(',')))
    SoilGrids().get_coverage_data(service_id=service_id, coverage_id=coverage_id, crs=crs,
                                  west=west, south=south, east=east, north=north, output=output)
    if os.path.isfile(output):
        print('Done')

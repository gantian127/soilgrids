from .soilgrids import SoilGrids
from .bmi import BmiSoilGrids
from ._version import get_versions

__all__ = ["SoilGrids", "BmiSoilGrids"]

__version__ = get_versions()['version']
del get_versions

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

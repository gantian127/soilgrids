```{image} _static/soilgrids_logo.png
:align: center
:alt: soilgrids
:scale: 22%
:target: https://soilgrids.readthedocs.io/
```

[soilgrids package][soilgrids-github] provides a set of functions that allow downloading of
the global gridded soil information from [SoilGrids][soilgrids-isric],
a system for global digital soil mapping to map the spatial distribution of soil properties across the globe.

soilgrids package includes a [Basic Model Interface (BMI)][bmi-docs],
which converts the SoilGrids dataset into a reusable,
plug-and-play data component ([pymt_soilgrids][soilgrids-pymt] for
the [PyMT][pymt-docs] modeling framework developed
by Community Surface Dynamics Modeling System ([CSDMS][csdms]).

# Installation

**Stable Release**

The soilgrids package and its dependencies can be installed with either *pip* or *conda*,

````{tab} pip
```console
pip install soilgrids
```
````

````{tab} conda
```console
conda install -c conda-forge soilgrids
```
````

**From Source**

After downloading the source code, run the following command from top-level folder
to install soilgrids.

```console
pip install -e .
```

# Citation
Please include the following references when citing this software package:

Gan, T., Tucker, G.E., Hutton, E.W.H., Piper, M.D., Overeem, I., Kettner, A.J.,
Campforts, B., Moriarty, J.M., Undzis, B., Pierce, E., McCready, L., 2024:
CSDMS Data Components: data–model integration tools for Earth surface processes
modeling. Geosci. Model Dev., 17, 2165–2185. https://doi.org/10.5194/gmd-17-2165-2024

Gan, T. (2023). CSDMS SoilGrids Data Component. Zenodo.
https://doi.org/10.5281/zenodo.10368882

# Quick Start

Below shows how to use two methods to download the SoilGrids datasets.

You can learn more details from the [tutorial notebook][soilgrids-notebook].
To run this notebook, please go to the [CSDMS EKT Lab][soilgrids-csdms] and follow
the instruction in the "Lab notes" section.

**Example 1**: use SoilGrids class to download data (Recommended method)

```python
import matplotlib.pyplot as plt
from soilgrids import SoilGrids

# get data from SoilGrids
soil_grids = SoilGrids()
data = soil_grids.get_coverage_data(
    service_id="phh2o",
    coverage_id="phh2o_0-5cm_mean",
    west=-1784000,
    south=1356000,
    east=-1140000,
    north=1863000,
    crs="urn:ogc:def:crs:EPSG::152160",
    output="test.tif",
)

# show metadata
for key, value in soil_grids.metadata.items():
    print(f"{key}: {value}")


# plot data
data.plot(figsize=(9, 5), vmin=0)
plt.title("Mean pH between 0 and 5 cm soil depth in Senegal")
```

```{image} _static/tif_plot.png
```

**Example 2**: use BmiSoilGrids class to download data (Demonstration of how to use BMI).

```python
import matplotlib.pyplot as plt
import numpy as np

from soilgrids.bmi import BmiSoilGrids


# initiate a data component
data_comp = BmiSoilGrids()
data_comp.initialize("config_file.yaml")

# get variable info
var_name = data_comp.get_output_var_names()[0]
var_unit = data_comp.get_var_units(var_name)
var_location = data_comp.get_var_location(var_name)
var_type = data_comp.get_var_type(var_name)
var_grid = data_comp.get_var_grid(var_name)

print(f"{var_name=}")
print(f"{var_unit=}")
print(f"{var_location=}")
print(f"{var_type=}")
print(f"{var_grid=}")

# get variable grid info
grid_rank = data_comp.get_grid_rank(var_grid)

grid_size = data_comp.get_grid_size(var_grid)

grid_shape = np.empty(grid_rank, int)
data_comp.get_grid_shape(var_grid, grid_shape)

grid_spacing = np.empty(grid_rank)
data_comp.get_grid_spacing(var_grid, grid_spacing)

grid_origin = np.empty(grid_rank)
data_comp.get_grid_origin(var_grid, grid_origin)

print(f"{grid_rank=}")
print(f"{grid_size=}")
print(f"{grid_shape=}")
print(f"{grid_spacing=}")
print(f"{grid_origin=}")

# get variable data
data = np.empty(grid_size, var_type)
data_comp.get_value(var_name, data)
data_2D = data.reshape(grid_shape)

# get X, Y extent for plot
min_y, min_x = grid_origin
max_y = min_y + grid_spacing[0] * (grid_shape[0] - 1)
max_x = min_x + grid_spacing[1] * (grid_shape[1] - 1)
dy = grid_spacing[0] / 2
dx = grid_spacing[1] / 2
extent = [min_x - dx, max_x + dx, min_y - dy, max_y + dy]

# plot data
fig, ax = plt.subplots(1, 1, figsize=(9, 5))
im = ax.imshow(data_2D, extent=extent, vmin=0)
fig.colorbar(im)
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Mean pH between 0 and 5 cm soil depth in Senegal")

# finalize data component
data_comp.finalize()
```

# Parameter settings

"get_coverage_data()" method includes multiple parameters for data download. Details for each parameter are listed below.

- **service_id**: The identifier of each map service provided by the SoilGrids system. The supported service id and the
  corresponding variable names are shown below. The "map_services" attribute of an instance will show more
  detailed information.

  - bdod: Bulk density
  - cec: Citation exchange capacity at ph7
  - cfvo: Coarse fragments volumetric
  - clay: Clay content
  - nitrogen: Nitrogen
  - phh2o: Soil pH in H2O
  - sand: Sand content
  - silt: Silt content
  - soc: Soil organic carbon content
  - ocs: Soil organic carbon stock
  - ocd: Organic carbon densities
  - wrb: World Reference Base (WRB) classes and probabilities

- **coverage_id**: The identifier of a coverage(map) from a map service. Each map service supports
  multiple coverages. To get a list of the coverage id from a map service, use "get_coverage_list()" method.
  To learn the meaning of the coverage id, please visit the SoilGrids [FAQ page][isric-faq]

- **crs**: the coordinate system code of a coverage. To get the supported crs code list of a coverage, use "get_coverage_info()" method.

- **west, south, east, north**: The bounding box values for the downloaded data. These values should be based on the
  coordinate system specified by the "crs" parameter. The west and south values are for the point on the lower left corner
  of the bounding box. The east and north values are for the point on the upper right corner of the bounding box.

- **output**: The file path of the GeoTiff file to store the downloaded data with ".tif" file extension.

- **resx, resy**: The grid resolution for the downloaded data when "crs" parameter is set as a
  projection coordinate system(e.g., epsg 152160). The default value for resx and resy is set as 250 (m) if not
  specified by the user. This is the same grid resolution as the soil datasets in the SoilGrids system.
  The resx and resy parameters are required when the "crs" parameter is set as a projection coordinate system
  and the width and height values are not needed.

- **width, height**: The width and height of the raster for the downloaded data when "crs" parameter is set as a
  geographic coordinate system(e.g., epsg 4326 for WGS84). The height represents the number of rows and the width
  represents the number of columns for the raster grid of the downloaded data. The width and height parameters
  are required when the "crs" is set as a geographic coordinate system and resx and resy values are not needed.

- **response_crs**: the coordinate system code for the GeoTiff file of the downloaded data. If response_crs is not
  specified by the user, its value will be the same as the crs value.

- **local_file**: indicate whether to make it priority to get the data by loading a local file that matches with the
  output file path. Default value is set as False, which means the function will directly download the data from SoilGrids
  system. If value is set as True, the function will first try to open a local file that matches with
  the output file path. And if the local file doesn't exist, it will then download data from SoilGrids.

<!-- links -->
[bmi-docs]: https://bmi.readthedocs.io
[csdms]: https://csdms.colorado.edu
[isric-faq]: https://www.isric.org/explore/soilgrids
[pymt-docs]: https://pymt.readthedocs.io
[soilgrids-csdms]: https://csdms.colorado.edu/wiki/Lab-0019
[soilgrids-github]: https://github.com/gantian127/soilgrids
[soilgrids-isric]: https://www.isric.org/explore/soilgrids
[soilgrids-notebook]: https://github.com/gantian127/soilgrids/blob/master/notebooks/soilgrids.ipynb
[soilgrids-pymt]: https://pymt-soilgrids.readthedocs.io

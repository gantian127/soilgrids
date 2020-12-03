from setuptools import setup, find_packages
import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="soilgrids",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Tian Gan",
    author_email="jamy127@foxmail.com",
    description="Fetch global gridded soil information from the "
                "SoilGrids system https://www.isric.org/explore/soilgrids",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="http://csdms.colorado.edu",
    packages=find_packages(exclude=("tests*",)),
    install_requires=open("requirements.txt", "r").read().splitlines(),
    entry_points={"console_scripts": ["soilgrids=soilgrids.cli:main"]},
)

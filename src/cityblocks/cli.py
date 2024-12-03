import os
import subprocess
import click

import geopandas as gpd
from ._core import extract_area, substitute_tiles


@click.group()
def cli():
    pass


@cli.command()
def download():
    """Download global LCZ map from Demuzere et al.

    The dataset is available on Zenodo under DOI
    https://doi.org/10.5281/zenodo.7670653
    """
    filename = "CGLC_MODIS_LCZ.tif"
    url = "https://zenodo.org/records/7670653/files/CGLC_MODIS_LCZ.tif?download=1"

    if os.path.exists(filename):
        click.echo(f"{filename} already exists, skipping download.")
    else:
        click.echo(
            "Downloading global dataset from https://doi.org/10.5281/zenodo.7670653"
        )
        subprocess.run(["curl", "-L", url, "-o", filename], check=True)
        click.echo(f"Download complete. Output stored as {filename}")


@cli.command()
@click.argument("bbox", type=str)
@click.option(
    "--outfile",
    default="lcz_subset.gpkg",
    help="Output file name",
    type=click.Path(),
)
def extract(bbox, outfile):
    """Extract area from global dataset and store as geopackage.

    BBOX should be a string like "east,south,west,north". You can generate a
    bounding box visually for example at http://bboxfinder.com/.

    For example:

        cityblocks extract "4.724808,52.273620,5.182114,52.458729" cityblocks
        extract --outfile lcz_amsterdam.gpkg
        "52.346876,4.755363,52.435083,4.985733"
    """
    click.echo(f"Extracting area {bbox}")

    filename = "CGLC_MODIS_LCZ.tif"
    if not os.path.exists(filename):
        raise FileNotFoundError(
            f"Cannot find input file {filename}. It can be downloaded with `cityblocks.download`."
        )

    gdf = extract_area(filename, bbox)
    gdf.to_file(outfile, driver="GPKG")

    click.echo(f"Done. Subset stored as {outfile}.")


@cli.command()
@click.option(
    "--infile",
    default="lcz_subset.gpkg",
    help="Input file name",
    type=click.Path(exists=True),
)
@click.option(
    "--outfile",
    default="lcz_tiles.gpkg",
    help="Output file name",
    type=click.Path(),
)
def convert(infile, outfile):
    """Convert pixel data to 2D tiles.

    Replace pixel coordinates with 2D tiles corresponding to the LCZ class, and
    add height column to data. The resulting output data can easily be
    visualized in QGIS, for example.
    """
    click.echo(f"Converting pixel coordinates in {infile}.")
    gdf = gpd.read_file("lcz_subset.gpkg")
    gdf = substitute_tiles(gdf)
    gdf.to_file(outfile, driver="GPKG")
    click.echo(f"Done. LCZ tiles stores as {outfile}.")
    click.echo("Now you can proceed to display the data in QGIS or elsewhere.")

import numpy as np
import rasterio
import geopandas as gpd
from shapely.affinity import translate
from importlib.resources import files

LCZ_HEIGHTS = {
    51: 37.5,
    52: 17.5,
    53: 6.5,
    54: 37.5,
    55: 17.5,
    56: 6.5,
    57: 3.0,
    58: 6.5,
    59: 6.5,
    60: 10.0,
    61: 10.0,
}

# TODO: combine them in a single file?
tiles = files("cityblocks")
_tile1 = gpd.read_file(f"{tiles}/tile_1_wgs84_51_52_53.gpkg").geometry.item()
_tile2 = gpd.read_file(f"{tiles}/tile_2_wgs84_54_55_56.gpkg").geometry.item()
_tile3 = gpd.read_file(f"{tiles}/tile_3_wgs84_57.gpkg").geometry.item()
_tile4 = gpd.read_file(f"{tiles}/tile_4_wgs84_58.gpkg").geometry.item()
_tile5 = gpd.read_file(f"{tiles}/tile_5_wgs84_59.gpkg").geometry.item()
_tile6 = gpd.read_file(f"{tiles}/tile_6_wgs84_60.gpkg").geometry.item()
LCZ_MULTIPOLYGONS = {
    51: _tile1,
    52: _tile1,
    53: _tile1,
    54: _tile2,
    55: _tile2,
    56: _tile2,
    57: _tile3,  
    58: _tile4,
    59: _tile5,
    60: _tile6,
    # 61: _tile7,  # Haven't needed it yet
}


def extract_area(filename, bbox):
    """Extract area and store as geopackage."""

    with rasterio.open(filename) as file:
        west, south, east, north = map(float, bbox.split(","))

        # Extract window
        window = (
            rasterio.windows.from_bounds(west, south, east, north, file.transform)
            .round_offsets()
            .round_lengths()
        )
        data = file.read(1, window=window)

        # Get coordinates
        height, width = data.shape
        rows, cols = np.meshgrid(np.arange(height), np.arange(width), indexing="ij")
        window_transform = rasterio.windows.transform(window, file.transform)
        coords = rasterio.transform.xy(window_transform, rows, cols, offset="center")
        x = np.array(coords[0])
        y = np.array(coords[1])

        # Create geopandas dataframe
        gdf = gpd.GeoDataFrame(
            data.ravel(),
            geometry=gpd.points_from_xy(x.ravel(), y.ravel()),
            crs=file.crs,
            columns=["LCZ"],
        )

        return gdf


def _get_tile_at_coords(row):
    """Look up the tile template and move it to the given coordinate."""
    # Extract information from dataframe row
    lcz_type = row["LCZ"]
    x = row.geometry.x
    y = row.geometry.y

    # Look up the tile template corresonding to the LCZ class
    tile = LCZ_MULTIPOLYGONS.get(lcz_type)
    tile_x = tile.centroid.x
    tile_y = tile.centroid.y

    # Return a copy of the tile centered on the given coordinate
    return translate(tile, xoff=(x - tile_x), yoff=(y - tile_y))


def substitute_tiles(gdf):
    """Replace pixel coordinates with 2D tiles corresponding to the LCZ class.

    Args:
        gdf: geopandas dataframe with LCZ column and pixel coordinateas as
        geometry.

    Note:
        Also adds a height column to the dataframe and discards any non-urban
        pixels.
    """
    # Discard non-urban landuse classes
    gdf = gdf.where(gdf["LCZ"] > 50).dropna()

    # Add height column
    gdf["height"] = gdf["LCZ"].map(LCZ_HEIGHTS).fillna(0)

    # Add polygons
    new_geometry = gdf.apply(_get_tile_at_coords, axis=1)
    gdf.geometry = new_geometry

    return gdf

import numpy as np
import rasterio
import geopandas as gpd
from shapely.affinity import translate

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

_tile1 = gpd.read_file("lcz_tiles/tile_1_wgs84_51_52_53.gpkg").geometry.item()
_tile2 = gpd.read_file("lcz_tiles/tile_2_wgs84_54_55_56.gpkg").geometry.item()
_tile3 = gpd.read_file("lcz_tiles/tile_3_wgs84_58.gpkg").geometry.item()
_tile4 = gpd.read_file("lcz_tiles/tile_4_wgs84_59.gpkg").geometry.item()
_tile5 = gpd.read_file("lcz_tiles/tile_5_wgs84_60.gpkg").geometry.item()
LCZ_MULTIPOLYGONS = {
    51: _tile1,
    52: _tile1,
    53: _tile1,
    54: _tile2,
    55: _tile2,
    56: _tile2,
    # 57: _tile3,  # Haven't needed it yet
    58: _tile3,
    59: _tile4,
    60: _tile5,
    # 61: _tile6,  # Haven't needed it yet
}


def get_tile_at_coords(row):
    """Look up the tile template and move it to the given coordinate.

    Input is a row of a geopandas dataframe with columns "LCZ" and point
    geometry. The points should represent grid cell centers.
    """
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


if __name__ == "__main__":
    # http://bboxfinder.com/#52.273620,4.724808,52.458729,5.182114
    filename = "../cityjson/CGLC_MODIS_LCZ.tif"
    bbox = "4.724808,52.273620,5.182114,52.458729"

    with rasterio.open(filename) as file:
        west, south, east, north = map(float, bbox.split(","))

        # Extract window
        window = rasterio.windows.from_bounds(west, south, east, north, file.transform)
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

        # Discard non-urban landuse classes
        gdf = gdf.where(gdf["LCZ"] > 50).dropna()

        # Add height column
        gdf["height"] = gdf["LCZ"].map(LCZ_HEIGHTS).fillna(0)

        # Add polygons
        new_geometry = gdf.apply(get_tile_at_coords, axis=1)
        gdf.geometry = new_geometry

        # Save
        gdf.to_file("lcz_subset.gpkg", driver="GPKG")

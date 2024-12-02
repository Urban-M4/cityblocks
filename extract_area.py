import numpy as np
import rasterio
import geopandas as gpd

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

        # Add height column
        gdf["height"] = gdf["LCZ"].map(LCZ_HEIGHTS).fillna(0)
        quit()

        # Save
        gdf.to_file("lcz_subset.gpkg", driver="GPKG")

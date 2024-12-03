# Cityblocks

Python project to:

- Download global LCZ map from [Demuzere et al.](https://zenodo.org/records/7670653).
- Extract an area of interest
- Generate a new dataset where each pixel is replaced by a 2D tile corresponding to the LCZ type

The generated file can be displayed in QGIS in 3D with the style specs that are shipped with the repository.

## How to use

```sh
pip install cityblocks
```

```python
# Download global LCZ data
cityblocks download

# Extract area of interest
cityblocks extract ....

# Convert LCZ data to 2d tiles
cityblocks convert
```

Then, import the dataset in QGIS and visualize it with ...

TODO: add instructions/screencast for plotting in QGIS

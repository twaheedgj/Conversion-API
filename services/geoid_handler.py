import rasterio

def get_geoid_height(lat, lon, tif_path):
    with rasterio.open(tif_path) as dataset:
        coords = [(lon, lat)]
        values = list(dataset.sample(coords))
        return float(values[0][0])

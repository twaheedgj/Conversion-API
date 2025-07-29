from pyproj import Transformer

def convert_wgs84_to_utm40s(lat, lon):
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32740", always_xy=True)
    easting, northing = transformer.transform(lon, lat)
    return easting, northing

def convert_utm40s_to_wgs84(easting, northing):
    transformer = Transformer.from_crs("EPSG:32740", "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(easting, northing)
    return lat, lon

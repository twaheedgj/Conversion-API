from services.geoid_handler import get_geoid_height

def convert_ellipsoid_to_orthometric(lat, lon, h_ellipsoid, tif_path):
    N = get_geoid_height(lat, lon, tif_path)
    H = h_ellipsoid - N
    return H, N

def convert_orthometric_to_ellipsoid(lat, lon, h_orthometric, tif_path):
    N = get_geoid_height(lat, lon, tif_path)
    h = h_orthometric + N
    return h, N

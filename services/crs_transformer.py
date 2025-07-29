"""
Coordinate Reference System (CRS) Transformation Services

This module provides functions to transform coordinates between WGS84 geographic 
coordinates and UTM Zone 40S projected coordinates using PyProj transformers.

Author: Your Name
Date: 2025
"""

from pyproj import Transformer
from pyproj.exceptions import CRSError, ProjError
import logging
from typing import Tuple

# Configure logging
logger = logging.getLogger(__name__)

# Initialize transformers as module-level constants for better performance
try:
    WGS84_TO_UTM40S = Transformer.from_crs("EPSG:4326", "EPSG:32740", always_xy=True)
    UTM40S_TO_WGS84 = Transformer.from_crs("EPSG:32740", "EPSG:4326", always_xy=True)
    logger.info("CRS transformers initialized successfully")
except CRSError as e:
    logger.error(f"Failed to initialize CRS transformers: {e}")
    raise

def convert_wgs84_to_utm40s(lat: float, lon: float) -> Tuple[float, float]:
    """
    Convert WGS84 geographic coordinates to UTM Zone 40S projected coordinates.
    
    This function transforms latitude/longitude coordinates in the WGS84 datum
    (EPSG:4326) to easting/northing coordinates in UTM Zone 40S (EPSG:32740).
    
    Args:
        lat (float): Latitude in decimal degrees (-90 to 90)
        lon (float): Longitude in decimal degrees (-180 to 180)
        
    Returns:
        Tuple[float, float]: A tuple containing (easting, northing) in meters
        
    Raises:
        ValueError: If coordinates are outside valid ranges
        ProjError: If coordinate transformation fails
        
    Example:
        >>> easting, northing = convert_wgs84_to_utm40s(-25.0, 28.0)
        >>> print(f"UTM: {easting:.2f}E, {northing:.2f}N")
    """
    try:
        # Validate input ranges
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            raise ValueError(f"Coordinates must be numeric. Got lat={type(lat)}, lon={type(lon)}")
        
        if not (-90 <= lat <= 90):
            raise ValueError(f"Latitude {lat} outside valid range [-90, 90] degrees")
            
        if not (-180 <= lon <= 180):
            raise ValueError(f"Longitude {lon} outside valid range [-180, 180] degrees")
        
        # Perform transformation
        easting, northing = WGS84_TO_UTM40S.transform(lon, lat)
        
        # Validate output (basic sanity check for UTM Zone 40S)
        if not (160000 <= easting <= 834000):
            logger.warning(f"Easting {easting:.2f} outside typical Zone 40S range")
        
        if not (1100000 <= northing <= 10000000):
            logger.warning(f"Northing {northing:.2f} outside typical southern hemisphere range")
        
        logger.debug(f"WGS84({lat:.6f}, {lon:.6f}) -> UTM40S({easting:.2f}, {northing:.2f})")
        
        return float(easting), float(northing)
        
    except ValueError:
        raise
    except ProjError as e:
        logger.error(f"Projection error in WGS84 to UTM40S conversion: {e}")
        raise ProjError(f"Failed to convert WGS84({lat}, {lon}) to UTM40S: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in WGS84 to UTM40S conversion: {e}")
        raise RuntimeError(f"Coordinate transformation failed: {e}")

def convert_utm40s_to_wgs84(easting: float, northing: float) -> Tuple[float, float]:
    """
    Convert UTM Zone 40S projected coordinates to WGS84 geographic coordinates.
    
    This function transforms easting/northing coordinates in UTM Zone 40S 
    (EPSG:32740) to latitude/longitude coordinates in the WGS84 datum (EPSG:4326).
    
    Args:
        easting (float): UTM easting coordinate in meters
        northing (float): UTM northing coordinate in meters
        
    Returns:
        Tuple[float, float]: A tuple containing (latitude, longitude) in decimal degrees
        
    Raises:
        ValueError: If coordinates are invalid
        ProjError: If coordinate transformation fails
        
    Example:
        >>> lat, lon = convert_utm40s_to_wgs84(500000.0, 7234567.0)
        >>> print(f"WGS84: {lat:.6f}°, {lon:.6f}°")
    """
    try:
        # Validate input types
        if not isinstance(easting, (int, float)) or not isinstance(northing, (int, float)):
            raise ValueError(f"Coordinates must be numeric. Got easting={type(easting)}, northing={type(northing)}")
        
        # Basic range validation for UTM Zone 40S
        if easting < 0 or easting > 1000000:
            logger.warning(f"Easting {easting} outside reasonable UTM range")
            
        if northing < 0 or northing > 10000000:
            logger.warning(f"Northing {northing} outside reasonable UTM range")
        
        # Perform transformation
        lon, lat = UTM40S_TO_WGS84.transform(easting, northing)
        
        # Validate output ranges
        if not (-90 <= lat <= 90):
            raise ValueError(f"Transformation resulted in invalid latitude: {lat}")
            
        if not (-180 <= lon <= 180):
            raise ValueError(f"Transformation resulted in invalid longitude: {lon}")
        
        logger.debug(f"UTM40S({easting:.2f}, {northing:.2f}) -> WGS84({lat:.6f}, {lon:.6f})")
        
        return float(lat), float(lon)
        
    except ValueError:
        raise
    except ProjError as e:
        logger.error(f"Projection error in UTM40S to WGS84 conversion: {e}")
        raise ProjError(f"Failed to convert UTM40S({easting}, {northing}) to WGS84: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in UTM40S to WGS84 conversion: {e}")
        raise RuntimeError(f"Coordinate transformation failed: {e}")

def validate_utm_zone_coverage(lat: float, lon: float) -> bool:
    """
    Check if WGS84 coordinates fall within UTM Zone 40S coverage area.
    
    UTM Zone 40S covers longitudes from 54°E to 60°E in the southern hemisphere.
    
    Args:
        lat (float): Latitude in decimal degrees
        lon (float): Longitude in decimal degrees
        
    Returns:
        bool: True if coordinates are within zone coverage, False otherwise
    """
    return lat < 0 and 54 <= lon < 60

def get_transformation_info() -> dict:
    """
    Get information about the available coordinate transformations.
    
    Returns:
        dict: Information about supported CRS and transformations
    """
    return {
        "source_crs": {
            "epsg": 4326,
            "name": "WGS84 Geographic",
            "unit": "degrees"
        },
        "target_crs": {
            "epsg": 32740,
            "name": "UTM Zone 40S",
            "unit": "meters"
        },
        "zone_coverage": {
            "longitude_range": "54°E to 60°E",
            "hemisphere": "Southern",
            "description": "UTM Zone 40S covers parts of Africa and the Indian Ocean"
        }
    }

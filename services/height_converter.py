"""
Height Datum Conversion Services

This module provides functions to convert between ellipsoidal and orthometric heights
using geoid models. The conversions are based on the relationship:
    H (orthometric) = h (ellipsoidal) - N (geoid height)

Author: Your Name
Date: 2025
"""

from services.geoid_handler import get_geoid_height, GeoidError
import logging
from typing import Tuple

# Configure logging
logger = logging.getLogger(__name__)

def convert_ellipsoid_to_orthometric(
    lat: float, 
    lon: float, 
    h_ellipsoid: float, 
    tif_path: str
) -> Tuple[float, float]:
    """
    Convert ellipsoidal height to orthometric height using a geoid model.
    
    This function computes orthometric height (height above mean sea level) from
    ellipsoidal height (height above reference ellipsoid) using the formula:
    H = h - N, where N is the geoid height from the model.
    
    Args:
        lat (float): Latitude in decimal degrees
        lon (float): Longitude in decimal degrees  
        h_ellipsoid (float): Ellipsoidal height in meters
        tif_path (str): Path to the geoid model TIFF file
        
    Returns:
        Tuple[float, float]: A tuple containing (orthometric_height, geoid_separation)
        
    Raises:
        ValueError: If input parameters are invalid
        GeoidError: If geoid height cannot be determined
        
    Example:
        >>> h_ortho, geoid_sep = convert_ellipsoid_to_orthometric(-25.0, 28.0, 100.0, "egm2008.tif")
        >>> print(f"Orthometric height: {h_ortho:.3f}m, Geoid separation: {geoid_sep:.3f}m")
    """
    try:
        # Validate inputs
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            raise ValueError(f"Coordinates must be numeric. Got lat={type(lat)}, lon={type(lon)}")
            
        if not isinstance(h_ellipsoid, (int, float)):
            raise ValueError(f"Ellipsoidal height must be numeric. Got {type(h_ellipsoid)}")
            
        if not (-90 <= lat <= 90):
            raise ValueError(f"Latitude {lat} outside valid range [-90, 90] degrees")
            
        if not (-180 <= lon <= 180):
            raise ValueError(f"Longitude {lon} outside valid range [-180, 180] degrees")
            
        if not isinstance(tif_path, str) or not tif_path.strip():
            raise ValueError("Geoid model path must be a non-empty string")
        
        logger.debug(f"Converting ellipsoidal to orthometric: lat={lat:.6f}, lon={lon:.6f}, h={h_ellipsoid:.3f}")
        
        # Get geoid height at the specified location
        try:
            N = get_geoid_height(lat, lon, tif_path)
        except Exception as e:
            logger.error(f"Failed to get geoid height at ({lat}, {lon}): {e}")
            raise GeoidError(f"Cannot determine geoid height: {e}")
        
        # Calculate orthometric height: H = h - N
        H = h_ellipsoid - N
        
        # Validate result
        if abs(H) > 20000:  # Sanity check: no point on Earth should exceed 20km elevation
            logger.warning(f"Unusual orthometric height result: {H:.3f}m at ({lat:.6f}, {lon:.6f})")
        
        logger.debug(f"Conversion result: H={H:.3f}m, N={N:.3f}m")
        
        return float(H), float(N)
        
    except (ValueError, GeoidError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in ellipsoid to orthometric conversion: {e}")
        raise RuntimeError(f"Height conversion failed: {e}")

def convert_orthometric_to_ellipsoid(
    lat: float, 
    lon: float, 
    h_orthometric: float, 
    tif_path: str
) -> Tuple[float, float]:
    """
    Convert orthometric height to ellipsoidal height using a geoid model.
    
    This function computes ellipsoidal height (height above reference ellipsoid) from
    orthometric height (height above mean sea level) using the formula:
    h = H + N, where N is the geoid height from the model.
    
    Args:
        lat (float): Latitude in decimal degrees
        lon (float): Longitude in decimal degrees
        h_orthometric (float): Orthometric height in meters
        tif_path (str): Path to the geoid model TIFF file
        
    Returns:
        Tuple[float, float]: A tuple containing (ellipsoidal_height, geoid_separation)
        
    Raises:
        ValueError: If input parameters are invalid
        GeoidError: If geoid height cannot be determined
        
    Example:
        >>> h_ellip, geoid_sep = convert_orthometric_to_ellipsoid(-25.0, 28.0, 50.0, "egm2008.tif")
        >>> print(f"Ellipsoidal height: {h_ellip:.3f}m, Geoid separation: {geoid_sep:.3f}m")
    """
    try:
        # Validate inputs
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            raise ValueError(f"Coordinates must be numeric. Got lat={type(lat)}, lon={type(lon)}")
            
        if not isinstance(h_orthometric, (int, float)):
            raise ValueError(f"Orthometric height must be numeric. Got {type(h_orthometric)}")
            
        if not (-90 <= lat <= 90):
            raise ValueError(f"Latitude {lat} outside valid range [-90, 90] degrees")
            
        if not (-180 <= lon <= 180):
            raise ValueError(f"Longitude {lon} outside valid range [-180, 180] degrees")
            
        if not isinstance(tif_path, str) or not tif_path.strip():
            raise ValueError("Geoid model path must be a non-empty string")
        
        logger.debug(f"Converting orthometric to ellipsoidal: lat={lat:.6f}, lon={lon:.6f}, H={h_orthometric:.3f}")
        
        # Get geoid height at the specified location
        try:
            N = get_geoid_height(lat, lon, tif_path)
        except Exception as e:
            logger.error(f"Failed to get geoid height at ({lat}, {lon}): {e}")
            raise GeoidError(f"Cannot determine geoid height: {e}")
        
        # Calculate ellipsoidal height: h = H + N
        h = h_orthometric + N
        
        # Validate result
        if abs(h) > 20000:  # Sanity check: no point on Earth should exceed 20km elevation
            logger.warning(f"Unusual ellipsoidal height result: {h:.3f}m at ({lat:.6f}, {lon:.6f})")
        
        logger.debug(f"Conversion result: h={h:.3f}m, N={N:.3f}m")
        
        return float(h), float(N)
        
    except (ValueError, GeoidError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in orthometric to ellipsoid conversion: {e}")
        raise RuntimeError(f"Height conversion failed: {e}")

def get_geoid_separation(lat: float, lon: float, tif_path: str) -> float:
    """
    Get only the geoid separation at a given location.
    
    This is a convenience function that returns just the geoid height (separation)
    without performing any height conversions.
    
    Args:
        lat (float): Latitude in decimal degrees
        lon (float): Longitude in decimal degrees
        tif_path (str): Path to the geoid model TIFF file
        
    Returns:
        float: Geoid separation in meters
        
    Raises:
        ValueError: If input parameters are invalid
        GeoidError: If geoid height cannot be determined
    """
    try:
        # Validate inputs
        if not (-90 <= lat <= 90):
            raise ValueError(f"Latitude {lat} outside valid range [-90, 90] degrees")
            
        if not (-180 <= lon <= 180):
            raise ValueError(f"Longitude {lon} outside valid range [-180, 180] degrees")
        
        return get_geoid_height(lat, lon, tif_path)
        
    except Exception as e:
        logger.error(f"Failed to get geoid separation at ({lat}, {lon}): {e}")
        raise

def validate_height_conversion(
    lat: float, 
    lon: float, 
    h_input: float, 
    conversion_type: str
) -> bool:
    """
    Validate if height conversion parameters are reasonable.
    
    Args:
        lat (float): Latitude in decimal degrees
        lon (float): Longitude in decimal degrees
        h_input (float): Input height in meters
        conversion_type (str): Type of conversion ('ellipsoid_to_orthometric' or 'orthometric_to_ellipsoid')
        
    Returns:
        bool: True if parameters are valid for conversion
    """
    try:
        # Basic coordinate validation
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return False
            
        # Height range validation (Mount Everest is ~8848m, Mariana Trench ~-11000m)
        if not (-15000 <= h_input <= 15000):
            logger.warning(f"Height {h_input}m outside typical Earth elevation range")
            
        return True
        
    except Exception:
        return False

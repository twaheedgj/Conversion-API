"""
Geoid Model Data Handler

This module provides functions to access and interpolate geoid height data from
TIFF-formatted geoid models. It handles loading geoid data, coordinate sampling,
and error conditions related to geoid model access.

Author: Your Name
Date: 2025
"""

import rasterio
from rasterio.errors import RasterioIOError
import numpy as np
import os
import logging
from typing import Union, List, Tuple
from functools import lru_cache

# Configure logging
logger = logging.getLogger(__name__)

class GeoidError(Exception):
    """Custom exception for geoid-related errors."""
    pass

@lru_cache(maxsize=1)
def _get_geoid_dataset_info(tif_path: str) -> dict:
    """
    Cache geoid dataset information to avoid repeated file reads.
    
    Args:
        tif_path (str): Path to the geoid TIFF file
        
    Returns:
        dict: Dataset information including bounds, resolution, and metadata
    """
    try:
        with rasterio.open(tif_path) as dataset:
            info = {
                'bounds': dataset.bounds,
                'width': dataset.width,
                'height': dataset.height,
                'transform': dataset.transform,
                'crs': dataset.crs,
                'nodata': dataset.nodata,
                'dtypes': dataset.dtypes
            }
            logger.debug(f"Cached geoid dataset info for {tif_path}")
            return info
    except Exception as e:
        logger.error(f"Failed to read geoid dataset info: {e}")
        raise GeoidError(f"Cannot access geoid model: {e}")

def get_geoid_height(lat: float, lon: float, tif_path: str) -> float:
    """
    Get geoid height at a specific geographic location from a TIFF geoid model.
    
    This function samples the geoid model at the specified coordinates and returns
    the geoid separation (N) - the difference between the geoid and reference ellipsoid.
    
    Args:
        lat (float): Latitude in decimal degrees (-90 to 90)
        lon (float): Longitude in decimal degrees (-180 to 180)
        tif_path (str): Path to the geoid model TIFF file
        
    Returns:
        float: Geoid height/separation in meters
        
    Raises:
        GeoidError: If the geoid model cannot be accessed or coordinates are invalid
        ValueError: If coordinates are outside valid ranges
        FileNotFoundError: If the geoid model file does not exist
        
    Example:
        >>> geoid_height = get_geoid_height(-25.0, 28.0, "egm2008.tif")
        >>> print(f"Geoid separation: {geoid_height:.3f} meters")
    """
    try:
        # Validate inputs
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            raise ValueError(f"Coordinates must be numeric. Got lat={type(lat)}, lon={type(lon)}")
            
        if not (-90 <= lat <= 90):
            raise ValueError(f"Latitude {lat} outside valid range [-90, 90] degrees")
            
        if not (-180 <= lon <= 180):
            raise ValueError(f"Longitude {lon} outside valid range [-180, 180] degrees")
            
        if not isinstance(tif_path, str) or not tif_path.strip():
            raise ValueError("Geoid model path must be a non-empty string")
        
        # Check if file exists
        if not os.path.exists(tif_path):
            raise FileNotFoundError(f"Geoid model file not found: {tif_path}")
        
        logger.debug(f"Sampling geoid height at ({lat:.6f}, {lon:.6f}) from {tif_path}")
        
        # Sample the geoid model
        with rasterio.open(tif_path) as dataset:
            # Check if coordinates are within dataset bounds
            bounds = dataset.bounds
            if not (bounds.left <= lon <= bounds.right and bounds.bottom <= lat <= bounds.top):
                logger.warning(f"Coordinates ({lat}, {lon}) outside geoid model bounds {bounds}")
                # Still attempt sampling - rasterio will handle out-of-bounds
            
            # Sample at the coordinate
            coords = [(lon, lat)]
            try:
                values = list(dataset.sample(coords))
                geoid_value = values[0][0]
                
                # Check for no-data values
                if dataset.nodata is not None and geoid_value == dataset.nodata:
                    raise GeoidError(f"No geoid data available at coordinates ({lat}, {lon})")
                
                # Check for NaN or infinite values
                if not np.isfinite(geoid_value):
                    raise GeoidError(f"Invalid geoid value at coordinates ({lat}, {lon}): {geoid_value}")
                
                # Convert to float and validate reasonable range
                geoid_height = float(geoid_value)
                
                # Sanity check: geoid heights typically range from -100 to +100 meters
                if abs(geoid_height) > 200:
                    logger.warning(f"Unusual geoid height: {geoid_height:.3f}m at ({lat:.6f}, {lon:.6f})")
                
                logger.debug(f"Geoid height at ({lat:.6f}, {lon:.6f}): {geoid_height:.3f}m")
                
                return geoid_height
                
            except (IndexError, TypeError) as e:
                raise GeoidError(f"Failed to sample geoid model at ({lat}, {lon}): {e}")
                
    except (ValueError, FileNotFoundError, GeoidError):
        raise
    except RasterioIOError as e:
        logger.error(f"Rasterio error accessing geoid model: {e}")
        raise GeoidError(f"Cannot read geoid model {tif_path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in geoid height sampling: {e}")
        raise GeoidError(f"Geoid sampling failed: {e}")

def get_geoid_heights_bulk(
    coordinates: List[Tuple[float, float]], 
    tif_path: str
) -> List[float]:
    """
    Get geoid heights for multiple coordinates in a single operation.
    
    This function is more efficient than calling get_geoid_height() multiple times
    when processing many coordinates.
    
    Args:
        coordinates: List of (latitude, longitude) tuples
        tif_path (str): Path to the geoid model TIFF file
        
    Returns:
        List[float]: List of geoid heights corresponding to input coordinates
        
    Raises:
        GeoidError: If the geoid model cannot be accessed
        ValueError: If coordinates are invalid
    """
    try:
        if not coordinates:
            return []
            
        logger.debug(f"Bulk sampling {len(coordinates)} coordinates from {tif_path}")
        
        # Validate all coordinates first
        for i, (lat, lon) in enumerate(coordinates):
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError(f"Invalid coordinates at index {i}: ({lat}, {lon})")
        
        # Prepare coordinates for rasterio (lon, lat order)
        raster_coords = [(lon, lat) for lat, lon in coordinates]
        
        with rasterio.open(tif_path) as dataset:
            values = list(dataset.sample(raster_coords))
            
            results = []
            for i, value in enumerate(values):
                geoid_value = value[0]
                
                # Check for no-data values
                if dataset.nodata is not None and geoid_value == dataset.nodata:
                    raise GeoidError(f"No geoid data at coordinate index {i}: {coordinates[i]}")
                
                if not np.isfinite(geoid_value):
                    raise GeoidError(f"Invalid geoid value at index {i}: {geoid_value}")
                
                results.append(float(geoid_value))
            
            logger.debug(f"Successfully sampled {len(results)} geoid heights")
            return results
            
    except Exception as e:
        logger.error(f"Bulk geoid sampling failed: {e}")
        raise GeoidError(f"Bulk geoid sampling failed: {e}")

def validate_geoid_model(tif_path: str) -> dict:
    """
    Validate and get information about a geoid model file.
    
    Args:
        tif_path (str): Path to the geoid model TIFF file
        
    Returns:
        dict: Information about the geoid model including bounds, resolution, etc.
        
    Raises:
        GeoidError: If the model is invalid or inaccessible
    """
    try:
        if not os.path.exists(tif_path):
            raise FileNotFoundError(f"Geoid model file not found: {tif_path}")
        
        with rasterio.open(tif_path) as dataset:
            info = {
                'file_path': tif_path,
                'file_size_mb': os.path.getsize(tif_path) / (1024 * 1024),
                'width': dataset.width,
                'height': dataset.height,
                'bands': dataset.count,
                'bounds': {
                    'west': dataset.bounds.left,
                    'east': dataset.bounds.right,
                    'south': dataset.bounds.bottom,
                    'north': dataset.bounds.top
                },
                'resolution': {
                    'x': dataset.transform[0],
                    'y': abs(dataset.transform[4])
                },
                'crs': str(dataset.crs),
                'dtype': str(dataset.dtypes[0]),
                'nodata': dataset.nodata,
                'valid': True
            }
            
            # Test sample a point to ensure data is readable
            try:
                center_lat = (dataset.bounds.bottom + dataset.bounds.top) / 2
                center_lon = (dataset.bounds.left + dataset.bounds.right) / 2
                test_value = list(dataset.sample([(center_lon, center_lat)]))[0][0]
                info['sample_value'] = float(test_value)
            except Exception as e:
                logger.warning(f"Could not sample test point from geoid model: {e}")
                info['sample_value'] = None
            
            logger.info(f"Geoid model validation successful: {tif_path}")
            return info
            
    except Exception as e:
        logger.error(f"Geoid model validation failed: {e}")
        raise GeoidError(f"Invalid geoid model {tif_path}: {e}")

def clear_geoid_cache():
    """Clear the cached geoid dataset information."""
    _get_geoid_dataset_info.cache_clear()
    logger.debug("Geoid dataset cache cleared")

"""
Pydantic models for API request and response data validation.

This module defines the data structures used for coordinate conversion requests
and responses, including validation rules and example data.
"""

from pydantic import BaseModel, Field
from typing import Optional

class WGS84Input(BaseModel):
    """Input model for WGS84 geographic coordinates."""
    
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Latitude in decimal degrees",
        example=24.8607
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitude in decimal degrees",
        example=67.0011
    )
    ellipsoid_height: Optional[float] = Field(
        None,
        description="Ellipsoidal height in meters (optional)",
        example=85.0
    )
    
    class Config:
        schema_extra = {
            "example": {
                "latitude": 24.8607,
                "longitude": 67.0011,
                "ellipsoid_height": 85.0
            }
        }

class UTM40SInput(BaseModel):
    """Input model for UTM Zone 40S projected coordinates."""
    
    easting: float = Field(
        ...,
        description="UTM easting coordinate in meters",
        example=345678.0
    )
    northing: float = Field(
        ...,
        description="UTM northing coordinate in meters",
        example=2754321.0
    )
    orthometric_height: Optional[float] = Field(
        None,
        description="Orthometric height in meters (optional)",
        example=50.0
    )
    
    class Config:
        schema_extra = {
            "example": {
                "easting": 345678.0,
                "northing": 2754321.0,
                "orthometric_height": 50.0
            }
        }

class WGS84Response(BaseModel):
    """Response model for WGS84 geographic coordinates with height information."""
    
    latitude: float = Field(
        ...,
        description="Latitude in decimal degrees",
        example=24.8607
    )
    longitude: float = Field(
        ...,
        description="Longitude in decimal degrees",
        example=67.0011
    )
    ellipsoid_height: float = Field(
        ...,
        description="Ellipsoidal height in meters",
        example=85.5
    )
    geoid_separation: Optional[float] = Field(
        None,
        description="Geoid separation (geoid height) in meters",
        example=-35.5
    )

    class Config:
        exclude_none = True
        schema_extra = {
            "example": {
                "latitude": 24.8607,
                "longitude": 67.0011,
                "ellipsoid_height": 85.5,
                "geoid_separation": -35.5
            }
        }

class UTM40SResponse(BaseModel):
    """Response model for UTM Zone 40S projected coordinates with height information."""
    
    easting: float = Field(
        ...,
        description="UTM easting coordinate in meters",
        example=1513689.55
    )
    northing: float = Field(
        ...,
        description="UTM northing coordinate in meters",
        example=12786972.88
    )
    orthometric_height: float = Field(
        ...,
        description="Orthometric height in meters",
        example=129.17
    )
    geoid_separation: Optional[float] = Field(
        None,
        description="Geoid separation (geoid height) in meters",
        example=-44.17
    )

    class Config:
        exclude_none = True
        schema_extra = {
            "example": {
                "easting": 1513689.55,
                "northing": 12786972.88,
                "orthometric_height": 129.17,
                "geoid_separation": -44.17
            }
        }

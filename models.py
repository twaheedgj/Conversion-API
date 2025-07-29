from pydantic import BaseModel
from typing import Optional
# --- WGS84 input ---
class WGS84Input(BaseModel):
    latitude: float
    longitude: float
    ellipsoid_height: Optional[float] = None

# --- UTM40S input ---
class UTM40SInput(BaseModel):
    easting: float
    northing: float
    orthometric_height: Optional[float] = None

# --- WGS84 response ---
class WGS84Response(BaseModel):
    latitude: float
    longitude: float
    ellipsoid_height: float
    geoid_separation: Optional[float] = None

    class Config:
        exclude_none = True

# --- UTM40S response ---
class UTM40SResponse(BaseModel):
    easting: float
    northing: float
    orthometric_height: float
    geoid_separation: Optional[float] = None

    class Config:
        exclude_none = True

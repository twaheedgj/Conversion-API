from fastapi import APIRouter, HTTPException, UploadFile, File, status
from models import WGS84Input, UTM40SInput, WGS84Response, UTM40SResponse
from services.crs_transformer import convert_wgs84_to_utm40s, convert_utm40s_to_wgs84
from services.height_converter import convert_ellipsoid_to_orthometric, convert_orthometric_to_ellipsoid
from config import settings
from fastapi.responses import StreamingResponse
import pandas as pd
import io
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/convert/wgs84-to-utm40s", 
    response_model=UTM40SResponse,
    summary="Convert WGS84 to UTM Zone 40S",
    description="""
    Convert WGS84 geographic coordinates (latitude, longitude) to UTM Zone 40S projected coordinates.
    
    - **latitude**: Latitude in decimal degrees (-90 to 90)
    - **longitude**: Longitude in decimal degrees (-180 to 180) 
    - **ellipsoid_height**: Optional ellipsoidal height in meters
    
    Returns UTM coordinates with orthometric height and geoid separation.
    """,
    responses={
        200: {"description": "Successful conversion"},
        400: {"description": "Invalid input coordinates"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error during conversion"}
    }
)
def wgs84_to_utm40s(input: WGS84Input) -> UTM40SResponse:
    """
    Convert WGS84 coordinates to UTM Zone 40S with orthometric height.
    
    Args:
        input: WGS84Input containing latitude, longitude, and optional ellipsoid height
        
    Returns:
        UTM40SResponse: Converted coordinates with orthometric height and geoid separation
        
    Raises:
        HTTPException: For invalid coordinates or processing errors
    """
    try:
        # Validate coordinate ranges
        if not (-90 <= input.latitude <= 90):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid latitude: {input.latitude}. Must be between -90 and 90 degrees."
            )
        
        if not (-180 <= input.longitude <= 180):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid longitude: {input.longitude}. Must be between -180 and 180 degrees."
            )
        
        logger.info(f"Converting WGS84 coordinates: lat={input.latitude}, lon={input.longitude}")
        
        # Convert coordinates
        east, north = convert_wgs84_to_utm40s(input.latitude, input.longitude)
        
        # Handle optional ellipsoid height
        ellipsoid_height = input.ellipsoid_height if input.ellipsoid_height is not None else 0.0
        
        # Convert height
        h_orthometric, geoid = convert_ellipsoid_to_orthometric(
            input.latitude, input.longitude, ellipsoid_height, settings.GEOID_PATH
        )
        
        logger.info(f"Conversion successful: UTM=({east:.2f}, {north:.2f})")
        
        return UTM40SResponse(
            easting=east,
            northing=north,
            orthometric_height=h_orthometric,
            geoid_separation=geoid
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting WGS84 to UTM40S: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversion failed: {str(e)}"
        )


@router.post(
    "/convert/utm40s-to-wgs84", 
    response_model=WGS84Response,
    summary="Convert UTM Zone 40S to WGS84",
    description="""
    Convert UTM Zone 40S projected coordinates to WGS84 geographic coordinates.
    
    - **easting**: UTM easting coordinate in meters
    - **northing**: UTM northing coordinate in meters
    - **orthometric_height**: Optional orthometric height in meters
    
    Returns WGS84 coordinates with ellipsoidal height and geoid separation.
    """,
    responses={
        200: {"description": "Successful conversion"},
        400: {"description": "Invalid UTM coordinates"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error during conversion"}
    }
)
def utm40s_to_wgs84(input: UTM40SInput) -> WGS84Response:
    """
    Convert UTM Zone 40S coordinates to WGS84 with ellipsoidal height.
    
    Args:
        input: UTM40SInput containing easting, northing, and optional orthometric height
        
    Returns:
        WGS84Response: Converted coordinates with ellipsoidal height and geoid separation
        
    Raises:
        HTTPException: For invalid coordinates or processing errors
    """
    try:
        # Validate UTM coordinate ranges (rough validation for Zone 40S)
        if not (160000 <= input.easting <= 834000):  # Typical range for UTM Zone 40S
            logger.warning(f"UTM easting {input.easting} outside typical range for Zone 40S")
        
        if not (1100000 <= input.northing <= 10000000):  # Southern hemisphere range
            logger.warning(f"UTM northing {input.northing} outside typical range for southern hemisphere")
        
        logger.info(f"Converting UTM40S coordinates: easting={input.easting}, northing={input.northing}")
        
        # Convert coordinates
        lat, lon = convert_utm40s_to_wgs84(input.easting, input.northing)
        
        # Handle optional orthometric height
        orthometric_height = input.orthometric_height if input.orthometric_height is not None else 0.0
        
        # Convert height
        h_ellipsoid, geoid = convert_orthometric_to_ellipsoid(
            lat, lon, orthometric_height, settings.GEOID_PATH
        )
        
        logger.info(f"Conversion successful: WGS84=({lat:.6f}, {lon:.6f})")
        
        return WGS84Response(
            latitude=lat,
            longitude=lon,
            ellipsoid_height=h_ellipsoid,
            geoid_separation=geoid
        )
        
    except Exception as e:
        logger.error(f"Error converting UTM40S to WGS84: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversion failed: {str(e)}"
        )

@router.post(
    "/upload/wgs84-to-utm40s",
    summary="Batch convert WGS84 coordinates from file",
    description="""
    Upload a CSV or Excel file containing WGS84 coordinates for batch conversion to UTM Zone 40S.
    
    **Required columns:**
    - latitude: Latitude in decimal degrees
    - longitude: Longitude in decimal degrees
    - ellipsoid_height: Ellipsoidal height in meters (can be empty/null)
    
    **Supported file formats:** CSV (.csv), Excel (.xlsx, .xls)
    
    Returns a CSV file with converted coordinates.
    """,
    responses={
        200: {"description": "Successful batch conversion", "content": {"text/csv": {}}},
        400: {"description": "Invalid file format or missing columns"},
        413: {"description": "File too large"},
        422: {"description": "File processing error"},
        500: {"description": "Internal server error during batch processing"}
    }
)
def upload_wgs84_csv(file: UploadFile = File(...)) -> StreamingResponse:
    """
    Process uploaded file containing WGS84 coordinates and convert to UTM Zone 40S.
    
    Args:
        file: Uploaded CSV or Excel file with WGS84 coordinates
        
    Returns:
        StreamingResponse: CSV file with converted coordinates
        
    Raises:
        HTTPException: For file format issues, missing columns, or processing errors
    """
    try:
        # Validate file type
        allowed_types = [
            "text/csv", 
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}. Only CSV and Excel files are supported."
            )

        # Check file size (10MB limit)
        if hasattr(file, 'size') and file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 10MB limit."
            )

        logger.info(f"Processing uploaded file: {file.filename}")

        # Read file
        try:
            if file.filename and file.filename.endswith(".csv"):
                df = pd.read_csv(file.file)
            else:
                df = pd.read_excel(file.file)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error reading file: {str(e)}"
            )

        # Validate required columns
        required_columns = {"latitude", "longitude", "ellipsoid_height"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {missing_columns}. Required: {required_columns}"
            )

        # Validate data
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File contains no data rows."
            )

        logger.info(f"Processing {len(df)} rows from uploaded file")

        results = []
        errors = []
        
        for idx, row in df.iterrows():
            try:
                lat = float(row["latitude"]) if pd.notna(row["latitude"]) else None
                lon = float(row["longitude"]) if pd.notna(row["longitude"]) else None
                h_ellip = float(row.get("ellipsoid_height", 0.0)) if pd.notna(row.get("ellipsoid_height")) else 0.0

                # Validate coordinates
                if lat is None or lon is None:
                    errors.append(f"Row {idx + 2}: Missing latitude or longitude")
                    continue
                    
                if not (-90 <= lat <= 90):
                    errors.append(f"Row {idx + 2}: Invalid latitude {lat}")
                    continue
                    
                if not (-180 <= lon <= 180):
                    errors.append(f"Row {idx + 2}: Invalid longitude {lon}")
                    continue

                # Convert coordinates
                easting, northing = convert_wgs84_to_utm40s(lat, lon)
                h_orth, geoid_sep = convert_ellipsoid_to_orthometric(lat, lon, h_ellip, settings.GEOID_PATH)

                results.append({
                    "latitude": lat,
                    "longitude": lon,
                    "ellipsoid_height": h_ellip,
                    "easting": round(easting, 3),
                    "northing": round(northing, 3),
                    "orthometric_height": round(h_orth, 3),
                    "geoid_separation": round(geoid_sep, 3)
                })

            except Exception as e:
                errors.append(f"Row {idx + 2}: Conversion error - {str(e)}")
                continue

        # Log any errors but continue processing
        if errors:
            logger.warning(f"Encountered {len(errors)} errors during processing: {errors[:5]}")  # Log first 5 errors

        if not results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No valid rows could be processed. Errors: {errors[:10]}"
            )

        result_df = pd.DataFrame(results)

        # Convert to CSV in memory
        stream = io.StringIO()
        result_df.to_csv(stream, index=False)
        stream.seek(0)

        logger.info(f"Successfully processed {len(results)} rows")

        return StreamingResponse(
            io.BytesIO(stream.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=wgs84_to_utm40s_converted.csv"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in file upload processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File processing failed: {str(e)}"
        )
    

@router.post(
    "/upload/utm40s-to-wgs84",
    summary="Batch convert UTM Zone 40S coordinates from file",
    description="""
    Upload a CSV or Excel file containing UTM Zone 40S coordinates for batch conversion to WGS84.
    
    **Required columns:**
    - easting: UTM easting coordinate in meters
    - northing: UTM northing coordinate in meters
    
    **Optional columns:**
    - orthometric_height: Orthometric height in meters (can be empty/null, defaults to 0)
    
    **Supported file formats:** CSV (.csv), Excel (.xlsx, .xls)
    
    Returns a CSV file with converted coordinates.
    """,
    responses={
        200: {"description": "Successful batch conversion", "content": {"text/csv": {}}},
        400: {"description": "Invalid file format or missing columns"},
        413: {"description": "File too large"},
        422: {"description": "File processing error"},
        500: {"description": "Internal server error during batch processing"}
    }
)
def upload_utm40s_csv(file: UploadFile = File(...)) -> StreamingResponse:
    """
    Process uploaded file containing UTM Zone 40S coordinates and convert to WGS84.
    
    Args:
        file: Uploaded CSV or Excel file with UTM coordinates
        
    Returns:
        StreamingResponse: CSV file with converted coordinates
        
    Raises:
        HTTPException: For file format issues, missing columns, or processing errors
    """
    try:
        # Validate file type
        allowed_types = [
            "text/csv", 
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}. Only CSV and Excel files are supported."
            )

        # Check file size (10MB limit)
        if hasattr(file, 'size') and file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 10MB limit."
            )

        logger.info(f"Processing uploaded UTM file: {file.filename}")

        # Read file
        try:
            if file.filename and file.filename.endswith(".csv"):
                df = pd.read_csv(file.file)
            else:
                df = pd.read_excel(file.file)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error reading file: {str(e)}"
            )

        # Validate required columns
        required_columns = {"easting", "northing"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {missing_columns}. Required: {required_columns}, Optional: orthometric_height"
            )

        # Validate data
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File contains no data rows."
            )

        logger.info(f"Processing {len(df)} rows from uploaded UTM file")

        results = []
        errors = []

        for idx, row in df.iterrows():
            try:
                easting = float(row["easting"]) if pd.notna(row["easting"]) else None
                northing = float(row["northing"]) if pd.notna(row["northing"]) else None
                h_orth = float(row.get("orthometric_height", 0.0)) if pd.notna(row.get("orthometric_height")) else 0.0

                # Validate coordinates
                if easting is None or northing is None:
                    errors.append(f"Row {idx + 2}: Missing easting or northing")
                    continue

                # Convert coordinates
                lat, lon = convert_utm40s_to_wgs84(easting, northing)
                h_ellip, geoid_sep = convert_orthometric_to_ellipsoid(lat, lon, h_orth, settings.GEOID_PATH)

                results.append({
                    "easting": easting,
                    "northing": northing,
                    "orthometric_height": h_orth,
                    "latitude": round(lat, 6),
                    "longitude": round(lon, 6),
                    "ellipsoid_height": round(h_ellip, 3),
                    "geoid_separation": round(geoid_sep, 3)
                })

            except Exception as e:
                errors.append(f"Row {idx + 2}: Conversion error - {str(e)}")
                continue

        # Log any errors but continue processing
        if errors:
            logger.warning(f"Encountered {len(errors)} errors during UTM processing: {errors[:5]}")

        if not results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No valid rows could be processed. Errors: {errors[:10]}"
            )

        result_df = pd.DataFrame(results)

        # Convert to CSV in memory
        stream = io.StringIO()
        result_df.to_csv(stream, index=False)
        stream.seek(0)

        logger.info(f"Successfully processed {len(results)} UTM rows")

        return StreamingResponse(
            io.BytesIO(stream.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=utm40s_to_wgs84_converted.csv"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in UTM file upload processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"UTM file processing failed: {str(e)}"
        )

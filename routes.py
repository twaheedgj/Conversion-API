from fastapi import APIRouter, HTTPException, UploadFile, File
from models import WGS84Input, UTM40SInput, WGS84Response, UTM40SResponse
from services.crs_transformer import convert_wgs84_to_utm40s, convert_utm40s_to_wgs84
from services.height_converter import convert_ellipsoid_to_orthometric, convert_orthometric_to_ellipsoid
from config import settings
from fastapi.responses import StreamingResponse
import pandas as pd
import io
router = APIRouter()

@router.post("/convert/wgs84-to-utm40s", response_model=UTM40SResponse)
def wgs84_to_utm40s(input: WGS84Input):
    east, north = convert_wgs84_to_utm40s(input.latitude, input.longitude)
    ellipsoid_height = input.ellipsoid_height if input.ellipsoid_height is not None else 0.0
    h_orthometric, geoid = convert_ellipsoid_to_orthometric(
        input.latitude, input.longitude, ellipsoid_height, settings.GEOID_PATH
    )
    return UTM40SResponse(
        easting=east,
        northing=north,
        orthometric_height=h_orthometric,
        geoid_separation=geoid
    )


@router.post("/convert/utm40s-to-wgs84", response_model=WGS84Response)
def utm40s_to_wgs84(input: UTM40SInput):
    lat, lon = convert_utm40s_to_wgs84(input.easting, input.northing)
    orthometric_height = input.orthometric_height if input.orthometric_height is not None else 0.0
    h_ellipsoid, geoid = convert_orthometric_to_ellipsoid(
        lat, lon, orthometric_height, settings.GEOID_PATH
    )
    return WGS84Response(
        latitude=lat,
        longitude=lon,
        ellipsoid_height=h_ellipsoid,
        geoid_separation=geoid
    )

@router.post("/upload/wgs84-to-utm40s")
def upload_wgs84_csv(file: UploadFile = File(...)):
    if file.content_type not in ["text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
        raise HTTPException(status_code=400, detail="Only CSV or Excel files are supported.")

    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {e}")

    required_columns = {"latitude", "longitude", "ellipsoid_height"}
    if not required_columns.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"Missing required columns: {required_columns}")

    results = []
    for _, row in df.iterrows():
        lat = row["latitude"]
        lon = row["longitude"]
        h_ellip = row.get("ellipsoid_height", 0.0)
        if pd.isna(h_ellip):
            h_ellip = 0.0
        easting, northing = convert_wgs84_to_utm40s(lat, lon)
        h_orth, geoid_sep = convert_ellipsoid_to_orthometric(lat, lon, h_ellip, settings.GEOID_PATH)

        results.append({
            "latitude": lat,
            "longitude": lon,
            "ellipsoid_height": h_ellip,
            "easting": easting,
            "northing": northing,
            "orthometric_height": h_orth,
            "geoid_separation": geoid_sep
        })

    result_df = pd.DataFrame(results)

    # Convert to CSV in memory
    stream = io.StringIO()
    result_df.to_csv(stream, index=False)
    stream.seek(0)

    return StreamingResponse(stream, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=converted.csv"
    })
    

@router.post("/upload/utm40s-to-wgs84")
def upload_utm40s_csv(file: UploadFile = File(...)):
    if file.content_type not in ["text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
        raise HTTPException(status_code=400, detail="Only CSV or Excel files are supported.")

    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {e}")

    required_columns = {"easting", "northing", "orthometric_height"}  # orthometric_height is optional
    if not required_columns.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"Missing required columns: {required_columns}")

    results = []
    for _, row in df.iterrows():
        easting = row["easting"]
        northing = row["northing"]
        h_orth = row.get("orthometric_height", 0.0)
        if pd.isna(h_orth):
            h_orth = 0.0

        lat, lon = convert_utm40s_to_wgs84(easting, northing)
        h_ellip, geoid_sep = convert_orthometric_to_ellipsoid(lat, lon, h_orth, settings.GEOID_PATH)

        results.append({
            "easting": easting,
            "northing": northing,
            "orthometric_height": h_orth,
            "latitude": lat,
            "longitude": lon,
            "ellipsoid_height": h_ellip,
            "geoid_separation": geoid_sep
        })

    result_df = pd.DataFrame(results)

    stream = io.StringIO()
    result_df.to_csv(stream, index=False)
    stream.seek(0)

    return StreamingResponse(stream, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=utm40s_to_wgs84.csv"
    })

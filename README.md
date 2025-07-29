# Geospatial Coordinate Conversion API

A high-performance FastAPI-based service for converting geospatial coordinates between different coordinate reference systems and height datums. The API provides precise transformations between:

* **Horizontal Systems**: WGS84 (EPSG:4326) ↔ UTM Zone 40S (EPSG:32740)
* **Vertical Systems**: Ellipsoidal ↔ Orthometric height using EGM2008 geoid model

---

## Key Features

* **Coordinate System Transformations**:
  - WGS84 Geographic → UTM Zone 40S Projected + Orthometric height
  - UTM Zone 40S Projected + Orthometric height → WGS84 Geographic + Ellipsoidal height

* **Batch Processing**: Upload CSV/Excel files for bulk coordinate conversion
* **Precision Height Conversion**: Utilizes EGM2008 geoid model for accurate height transformations
* **Flexible Input Validation**: Height parameters are optional with intelligent fallback mechanisms
* **High Performance**: Built on FastAPI framework for optimal speed and scalability
* **Interactive Documentation**: Auto-generated API documentation with Swagger UI

---

## 📂 Project Structure

```
Conversion-API/
├── main.py
├── routes.py
├── models.py
├── config.py
├── .env                         ← Environment configuration
├── services/
│   ├── crs_transformer.py
│   ├── height_converter.py
│   └── geoid_handler.py
├── geoid_models/
│   └── us_nga_egm2008_1.tif   ← Your geoid model
├── requirements.txt
└── README.md
```

---

## Installation and Setup

### Prerequisites
- Python 3.10 or higher
- Git

### Step 1: Clone Repository

```bash
git clone https://github.com/twaheedgj/Conversion-API.git
cd Conversion-API
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Environment Configuration

Configure the geoid model path in your environment file:

```env
GEOID_PATH=geoid_models/us_nga_egm2008_1.tif
```

### Step 4: Launch Application

```bash
uvicorn main:app --reload
```

**Access Points:**
- API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Alternative Docs: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- Health Check: [http://localhost:8000/](http://localhost:8000/)

---

## API Reference

### Coordinate Conversion Endpoints

#### `POST /convert/wgs84-to-utm40s`

Transforms WGS84 geographic coordinates to UTM Zone 40S projected coordinates with orthometric height.

**Request Body:**
```json
{
  "latitude": 24.8607,
  "longitude": 67.0011,
  "ellipsoid_height": 85    // Optional
}
```

**Response:**
```json
{
  "easting": 1513689.5543600176,
  "northing": 12786972.878259797,
  "orthometric_height": 129.1711883544922,
  "geoid_separation": -44.17118835449219
}
```

#### `POST /convert/utm40s-to-wgs84`

Transforms UTM Zone 40S projected coordinates to WGS84 geographic coordinates with ellipsoidal height.

**Request Body:**
```json
{
  "easting": 345678,
  "northing": 2754321,
  "orthometric_height": 50    // Optional
}
```

**Response:**
```json
{
  "latitude": 24.8607,
  "longitude": 67.0011,
  "ellipsoid_height": 85.5,
  "geoid_separation": -35.5
}
```

### Batch Processing Endpoints

#### `POST /upload/wgs84-to-utm40s`

Processes CSV/Excel files containing WGS84 coordinates and returns converted UTM coordinates.

**Required Columns:** `latitude`, `longitude`, `ellipsoid_height`

#### `POST /upload/utm40s-to-wgs84`

Processes CSV/Excel files containing UTM coordinates and returns converted WGS84 coordinates.

**Required Columns:** `easting`, `northing`  
**Optional Columns:** `orthometric_height`

---

## Data Format Specifications

### CSV File Format Examples

**WGS84 to UTM Conversion:**
```csv
latitude,longitude,ellipsoid_height
24.8607,67.0011,85
25.2048,67.0308,92.5
```

**UTM to WGS84 Conversion:**
```csv
easting,northing,orthometric_height
345000,2750000,50
346000,2751000,52.3
```

### Supported File Types
- CSV (Comma-separated values)
- Excel (.xlsx, .xls)

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Web Framework** | FastAPI | High-performance async API framework |
| **Data Validation** | Pydantic | Request/response model validation |
| **Data Processing** | Pandas | CSV/Excel file processing and manipulation |
| **Coordinate Transformation** | PyProj | Coordinate reference system transformations |
| **Geospatial Processing** | Rasterio | Geoid model data access and interpolation |
| **Runtime** | Python 3.10+ | Core application runtime |

---

## Development Roadmap

### Planned Enhancements
- [ ] **Extended CRS Support**: Additional coordinate reference systems (EPSG codes)
- [ ] **Interactive Mapping**: Web-based coordinate visualization
- [ ] **Authentication System**: Secure API access controls
- [ ] **Custom Geoid Support**: User-uploadable geoid models
- [ ] **Performance Optimization**: Enhanced processing for large datasets
- [ ] **API Versioning**: Backwards-compatible API evolution

### Contributing
We welcome contributions! Please see our [contribution guidelines](CONTRIBUTING.md) for details on:
- Code standards and style guides
- Pull request procedures
- Issue reporting templates
- Development environment setup

---

## Related Projects

### Frontend Application
A companion web interface is available for interactive coordinate conversion:

**Repository**: [Conversion-API-UI](https://github.com/twaheedgj/Conversion-API-UI)

**Features:**
- Intuitive web interface for coordinate conversion
- Interactive map visualization with coordinate plotting
- Drag-and-drop file upload with real-time processing
- Responsive design for desktop and mobile devices

---

## Geoid Model Reference

### EGM2008 Implementation Details

| Specification | Value |
|---------------|-------|
| **Model Name** | Earth Gravitational Model 2008 (EGM2008) |
| **Source Authority** | U.S. National Geospatial-Intelligence Agency (NGA) |
| **Spatial Resolution** | 1° × 1° geographic grid |
| **Global Coverage** | Worldwide |
| **Data Source** | [Agisoft Geoids Collection](https://www.agisoft.com/downloads/geoids/) |
| **File Format** | GeoTIFF (.tif) |
| **Local Filename** | `us_nga_egm2008_1.tif` |


## Support and Community

### Getting Help
- **Documentation**: Comprehensive API docs at `/docs` endpoint
- **Issues**: [GitHub Issues](https://github.com/twaheedgj/Conversion-API/issues)
- **Discussions**: [GitHub Discussions](https://github.com/twaheedgj/Conversion-API/discussions)

### Reporting Issues
When reporting issues, please include:
- API version and endpoint used
- Sample input data and expected output
- Error messages and response codes
- System environment details

### Contact
For direct inquiries, please contact the maintainer through GitHub.

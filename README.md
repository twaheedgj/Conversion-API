# Geospatial Coordinate Conversion API

A high-performance FastAPI-based service for converting geospatial coordinates between different coordinate reference systems and height datums. The API provides precise transformations between:

* **Horizontal Systems**: WGS84 (EPSG:4326) ↔ UTM Zone 40S (EPSG:32740)
* **Vertical Systems**: Ellipsoidal ↔ Orthometric height using EGM2008 geoid model

---

## ✨ Key Features

* **🌍 Coordinate System Transformations**:
  - WGS84 Geographic → UTM Zone 40S Projected + Orthometric height
  - UTM Zone 40S Projected + Orthometric height → WGS84 Geographic + Ellipsoidal height

* **📊 Batch Processing**: Upload CSV/Excel files for bulk coordinate conversion
* **🎯 Precision Height Conversion**: Utilizes EGM2008 geoid model for accurate height transformations
* **🔧 Flexible Input Validation**: Height parameters are optional with intelligent fallback mechanisms
* **⚡ High Performance**: Built on FastAPI framework for optimal speed and scalability
* **📚 Interactive Documentation**: Auto-generated API documentation with Swagger UI
* **🛡️ Robust Error Handling**: Comprehensive validation and error reporting
* **📈 Health Monitoring**: Built-in health checks and API status monitoring

---

## 📂 Project Structure

```
Conversion-API/
├── main.py                      ← FastAPI application entry point
├── routes.py                    ← API endpoint definitions
├── models.py                    ← Pydantic data models
├── config.py                    ← Configuration settings
├── .env                         ← Environment configuration
├── services/
│   ├── crs_transformer.py      ← Coordinate reference system transformations
│   ├── height_converter.py     ← Height datum conversions
│   └── geoid_handler.py        ← EGM2008 geoid model processing
├── geoid_models/
│   └── us_nga_egm2008_1.tif   ← EGM2008 geoid model data
├── requirements.txt             ← Python dependencies
└── README.md                    ← This documentation
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (Recommended: Python 3.11)
- **Git** for version control
- **10GB+ free disk space** (for geoid model)

### Installation Steps

#### 1️⃣ Clone Repository
```bash
git clone https://github.com/twaheedgj/Conversion-API.git
cd Conversion-API
```

#### 2️⃣ Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4️⃣ Download Geoid Model
Download the EGM2008 geoid model from [Agisoft Geoids Collection](https://www.agisoft.com/downloads/geoids/) and place it in the `geoid_models/` directory as `us_nga_egm2008_1.tif`.

#### 5️⃣ Environment Configuration
Create a `.env` file with the following configuration:
```env
GEOID_PATH=geoid_models/us_nga_egm2008_1.tif
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

#### 6️⃣ Launch Application
```bash
uvicorn main:app --reload
```

### 🌐 Access Points
- **📖 API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **📋 Alternative Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **❤️ Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **ℹ️ API Information**: [http://localhost:8000/info](http://localhost:8000/info)

---

## 📖 API Reference

### 🔄 Coordinate Conversion Endpoints

#### `POST /convert/wgs84-to-utm40s`
**Description**: Transforms WGS84 geographic coordinates to UTM Zone 40S projected coordinates with orthometric height.

**Request Examples:**

*With ellipsoid height:*
```json
{
  "latitude": 24.8607,
  "longitude": 67.0011,
  "ellipsoid_height": 85
}
```

*Without height (coordinates only):*
```json
{
  "latitude": 24.8607,
  "longitude": 67.0011
}
```

**Response Example:**
```json
{
  "easting": 1513689.5543600176,
  "northing": 12786972.878259797,
  "orthometric_height": 129.1711883544922,
  "geoid_separation": -44.17118835449219
}
```

#### `POST /convert/utm40s-to-wgs84`
**Description**: Transforms UTM Zone 40S projected coordinates to WGS84 geographic coordinates with ellipsoidal height.

**Request Examples:**

*With orthometric height:*
```json
{
  "easting": 345678,
  "northing": 2754321,
  "orthometric_height": 50
}
```

*Without height (coordinates only):*
```json
{
  "easting": 345678,
  "northing": 2754321
}
```

**Response Example:**
```json
{
  "latitude": 24.8607,
  "longitude": 67.0011,
  "ellipsoid_height": 85.5,
  "geoid_separation": -35.5
}
```

### 📁 Batch Processing Endpoints

#### `POST /upload/wgs84-to-utm40s`
**Description**: Processes CSV/Excel files containing WGS84 coordinates and returns converted UTM coordinates.

**File Requirements:**
- **Required Columns**: `latitude`, `longitude`
- **Optional Columns**: `ellipsoid_height`
- **Supported Formats**: CSV, Excel (.xlsx, .xls)
- **Max File Size**: 10MB

#### `POST /upload/utm40s-to-wgs84`
**Description**: Processes CSV/Excel files containing UTM coordinates and returns converted WGS84 coordinates.

**File Requirements:**
- **Required Columns**: `easting`, `northing`
- **Optional Columns**: `orthometric_height`
- **Supported Formats**: CSV, Excel (.xlsx, .xls)
- **Max File Size**: 10MB

### 🏥 Utility Endpoints

#### `GET /health`
Returns API health status and component availability.

#### `GET /info`
Provides detailed API capabilities, configuration, and geoid model information.

---

## 📋 Data Format Specifications

### CSV File Format Examples

**WGS84 to UTM Conversion Input:**
```csv
latitude,longitude,ellipsoid_height
24.8607,67.0011,85
25.2048,67.0308,92.5
24.7234,66.9876,78.3
```

**UTM to WGS84 Conversion Input:**
```csv
easting,northing,orthometric_height
345000,2750000,50
346000,2751000,52.3
347000,2752000,48.7
```

### Input Validation Rules

| Parameter | Type | Range | Required |
|-----------|------|-------|----------|
| **latitude** | float | -90.0 to 90.0 | ✅ |
| **longitude** | float | -180.0 to 180.0 | ✅ |
| **ellipsoid_height** | float | No limits | ❌ |
| **easting** | float | Valid UTM range | ✅ |
| **northing** | float | Valid UTM range | ✅ |
| **orthometric_height** | float | No limits | ❌ |

---

## 🛠️ Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **🌐 Web Framework** | FastAPI | 0.104+ | High-performance async API framework |
| **📊 Data Validation** | Pydantic | 2.0+ | Request/response model validation |
| **🗃️ Data Processing** | Pandas | 2.0+ | CSV/Excel file processing and manipulation |
| **🗺️ Coordinate Transformation** | PyProj | 3.6+ | Coordinate reference system transformations |
| **🌍 Geospatial Processing** | Rasterio | 1.3+ | Geoid model data access and interpolation |
| **🔢 Numerical Computing** | NumPy | 1.24+ | Efficient numerical operations |
| **🐍 Runtime** | Python | 3.10+ | Core application runtime |

---

## 🗺️ Related Projects

### 🖥️ Frontend Application
A companion web interface is available for interactive coordinate conversion:

**🔗 Repository**: [Conversion-API-UI](https://github.com/twaheedgj/Conversion-API-UI.git)

**✨ Features:**
- 🎨 Intuitive web interface for coordinate conversion
- 🗺️ Interactive map visualization with coordinate plotting  
- 📁 Drag-and-drop file upload with real-time processing
- 📱 Responsive design for desktop and mobile devices
- ⚡ Real-time validation and conversion results

---

## 🌍 Geoid Model Reference

### EGM2008 Implementation Details

| Specification | Value |
|---------------|-------|
| **📊 Model Name** | Earth Gravitational Model 2008 (EGM2008) |
| **🏛️ Source Authority** | U.S. National Geospatial-Intelligence Agency (NGA) |
| **📐 Spatial Resolution** | 1° × 1° geographic grid |
| **🌐 Global Coverage** | Worldwide (-90° to +90° latitude) |
| **📁 Data Source** | [Agisoft Geoids Collection](https://www.agisoft.com/downloads/geoids/) |
| **💾 File Format** | GeoTIFF (.tif) |
| **📂 Local Filename** | `us_nga_egm2008_1.tif` |
| **⚖️ Accuracy** | ±1-2 meters globally |

**⚠️ Note**: Please ensure compliance with licensing terms when using the EGM2008 geoid model for commercial applications.

---

## 🚧 Development Roadmap

### 🎯 Planned Enhancements
- [ ] **🌍 Extended CRS Support**: Additional coordinate reference systems (EPSG codes)
- [ ] **🗺️ Interactive Mapping**: Web-based coordinate visualization
- [ ] **🔐 Authentication System**: Secure API access controls
- [ ] **📁 Custom Geoid Support**: User-uploadable geoid models
- [ ] **⚡ Performance Optimization**: Enhanced processing for large datasets
- [ ] **🔄 API Versioning**: Backwards-compatible API evolution
- [ ] **📊 Analytics Dashboard**: Usage statistics and performance metrics
- [ ] **🌐 Multi-language Support**: Internationalization capabilities

### 🤝 Contributing
We welcome contributions! Please see our contributing guidelines for details on:
- 📝 Code standards and style guides
- 🔄 Pull request procedures
- 🐛 Issue reporting templates
- 🛠️ Development environment setup

---

## 🆘 Support and Community

### 🤔 Getting Help
- **📚 Documentation**: Comprehensive API docs at `/docs` endpoint
- **🐛 Issues**: [Report bugs or request features](https://github.com/twaheedgj/Conversion-API/issues)
- **💬 Discussions**: [Community discussions](https://github.com/twaheedgj/Conversion-API/discussions)

### 🐛 Reporting Issues
When reporting issues, please include:
- 📋 API version and endpoint used
- 📊 Sample input data and expected output
- ❌ Error messages and response codes
- 💻 System environment details (OS, Python version)
- 📝 Steps to reproduce the issue

### 📧 Contact
**Maintainer**: Talha Waheed  
**Email**: talhawaheed7807@gmail.com  
**GitHub**: [@twaheedgj](https://github.com/twaheedgj)

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

**© 2025 Talha Waheed. All rights reserved.**

---

*Built with ❤️ using FastAPI and modern geospatial technologies.*

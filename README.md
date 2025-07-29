# 🌍 Geospatial Coordinate Conversion API

A FastAPI-based service to convert geospatial coordinates between horizontal and vertical coordinate systems. Supports:

* WGS84 (EPSG:4326) ↔ UTM Zone 40S (EPSG:32740)
* Ellipsoidal ↔ Orthometric height (via EGM2008 geoid model)

---

## 🛠️ Features

* 🔁 **Single-point conversion:**

  * WGS84 → UTM40S + Orthometric height
  * UTM40S + Orthometric height → WGS84 + Ellipsoidal height
* 📅 **Batch conversion via CSV/Excel file**
* 📏 Uses geoid model (EGM2008) for accurate height transformation
* ✅ Ellipsoidal/Orthometric height input is optional (fallback to geoid-based estimation)
* ⚡ Built with FastAPI for speed and scalability

---

## 📂 Project Structure

```
.
├── app/
│   ├── main.py
│   ├── routes.py
│   ├── models.py
│   ├── services/
│   │   ├── crs_transformer.py
│   │   └── height_converter.py
│   └── config.py
├── data/
│   └── egm2008_1.tif   ← Your geoid model
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run

### 1. Clone the repo

```bash
git clone https://github.com/your-username/geospatial-api.git
cd geospatial-api
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set geoid path in `config.py`

```python
GEOID_PATH = "data/egm2008_1.tif"
```

### 4. Start the server

```bash
uvicorn app.main:app --reload
```

Visit: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📢 API Endpoints

### 🔹 `POST /convert/wgs84-to-utm40s`

Convert WGS84 (lat/lon + optional ellipsoid height) → UTM40S + orthometric height

#### Sample Input:

```json
{
  "latitude": 24.8607,
  "longitude": 67.0011,
  "ellipsoid_height": 85
}
```

---

### 🔹 `POST /convert/utm40s-to-wgs84`

Convert UTM40S + optional orthometric height → WGS84 + ellipsoid height

#### Sample Input:

```json
{
  "easting": 345678,
  "northing": 2754321
}
```

---

### 🔹 `POST /upload/wgs84-to-utm40s`

Upload CSV/Excel with WGS84 data and receive UTM + orthometric height.

Required columns: `latitude`, `longitude`, `ellipsoid_height`

---

### 🔹 `POST /upload/utm40s-to-wgs84`

Upload CSV/Excel with UTM data and receive WGS84 + ellipsoid height.

Required columns: `easting`, `northing`
Optional: `orthometric_height`

---

## 📁 Sample CSV Format

**For `/upload/utm40s-to-wgs84`:**

```csv
easting,northing,orthometric_height
345000,2750000,50
346000,2751000,
```

**For `/upload/wgs84-to-utm40s`:**

```csv
latitude,longitude,ellipsoid_height
24.8607,67.0011,85
```

---

## ⚙️ Tech Stack

* 🐍 Python 3.10+
* ⚡ FastAPI
* 📦 Pydantic
* 📊 Pandas
* 🌍 Pyproj, Rasterio (for CRS + geoid transformation)

---

## 📌 To-Do / Future Enhancements

* 🌐 Support more CRS zones (EPSG codes)
* 🌍 Add frontend UI for uploads + visual map
* 📊 Visualization of coordinates on map
* 🔒 Authentication for secure API access
* 📅 Store/upload custom geoid files

---

## 📃 License

MIT License – feel free to use, fork, and contribute!

---

## 🤛 Need Help?

Feel free to [open an issue](https://github.com/twaheedgj/i/issues) or message the maintainer.

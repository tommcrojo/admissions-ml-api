# Admissions Data Engineering Pipeline

![PySpark](https://img.shields.io/badge/PySpark-3.5.0-E25A1C.svg)
![Databricks](https://img.shields.io/badge/Databricks-Platform-FF3621.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Data engineering pipeline for university admissions data using Databricks, PySpark, and the medallion architecture (Bronze → Silver → Gold).

## 🎯 Overview

This project demonstrates a production-ready data pipeline that transforms raw university admissions data into ML-ready features. The focus is on **data engineering practices** including data quality, feature engineering, and scalable processing using PySpark on Databricks.

The ML model and inference API serve as downstream consumers of the processed data, showcasing how data engineering enables analytics and machine learning.

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATABRICKS PLATFORM                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐        │
│  │    BRONZE    │      │    SILVER    │      │     GOLD     │        │
│  │  Raw Data    │ ───> │   Cleaned    │ ───> │  ML Features │        │
│  │              │      │ + Features   │      │              │        │
│  └──────────────┘      └──────────────┘      └──────────────┘        │
│         │                     │                     │                │
│         │                     │                     │                │
│    CSV Ingestion        Feature Engineering    Final Selection      │
│    Raw Storage          Normalization           ML-Ready              │
│                         Encoding                                      │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                          CONSUMERS                                      │
│                                                                         │
│  ┌──────────────┐                        ┌──────────────┐             │
│  │ ML Training  │                        │  Inference   │             │
│  │  (sklearn)   │                        │  API (FastAPI)│             │
│  └──────────────┘                        └──────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🔧 Pipeline Stages

### Bronze Layer: Raw Data Ingestion

**Notebook:** `00_load_data.py`

**Purpose:** Load raw CSV data from external sources into the data lakehouse.

**Operations:**
- CSV file reading with schema inference
- Data validation and initial quality checks
- Storage in `bronze.admissions_raw` table

**Source Schema:**
| Column | Type | Description |
|--------|------|-------------|
| dni | int | Student identifier |
| nombre | string | Student name |
| edad | int | Age |
| nota_acceso | double | Access exam grade (0-10) |
| rama_bachillerato | string | High school track |
| provincia | string | Province |
| es_extranjero | boolean | International student |
| modalidad | string | Study modality |
| programa_elegido | string | Chosen program |
| ano_ingreso | int | Year of entry |
| creditos_primera_matricula | int | Credits enrolled |
| exito_academico | int | Academic success (target) |

### Silver Layer: Data Cleaning & Feature Engineering

**Notebook:** `01_bronze_to_silver.py`

**Purpose:** Transform raw data into clean, feature-enriched data ready for analysis.

**Feature Transformations:**

| Feature | Formula | Rationale |
|---------|---------|-----------|
| `nota_normalizada` | `(nota_acceso - 5.0) / 5.0` | Normalize 0-10 scale to 0-1 |
| `rama_ciencias` | `IF(rama = "Ciencias", 1, 0)` | One-hot encoding |
| `rama_sociales` | `IF(rama = "Ciencias Sociales", 1, 0)` | One-hot encoding |
| `rama_ingenieria` | `IF(rama = "Ingeniería", 1, 0)` | One-hot encoding |
| `es_murcia` | `IF(provincia = "Murcia", 1, 0)` | Regional indicator |
| `es_online` | `IF(modalidad = "Online", 1, 0)` | Modality indicator |
| `creditos_ratio` | `creditos / 60.0` | Load relative to full-time |

**Output:** `silver.admissions_clean` table

### Gold Layer: ML-Ready Features

**Notebook:** `02_silver_to_gold.py`

**Purpose:** Select and format final features optimized for machine learning.

**Final Feature Set:**
- Identifier: `dni`, `programa_elegido`
- Target: `exito_academico`
- Numerical features: `nota_normalizada`, `edad`, `creditos_ratio`
- Encoded features: `rama_ciencias`, `rama_sociales`, `rama_ingenieria`, `es_murcia`, `es_online`, `es_extranjero`

**Output:** `gold.ml_features` table

## 📁 Project Structure

```
admissions-ml-api/
├── preprocessing/           # PySpark transformation modules
│   ├── __init__.py         # Pipeline orchestration
│   ├── bronze.py           # Raw data ingestion
│   ├── silver.py           # Cleaning & feature engineering
│   ├── gold.py             # ML-ready features
│   └── utils.py            # Utility functions
├── notebooks/              # Databricks notebooks (reference)
│   ├── 00_load_data.py
│   ├── 01_bronze_to_silver.py
│   ├── 02_silver_to_gold.py
│   └── 03_train_model.py
├── api/                    # Inference API (consumes gold layer)
│   └── main.py
├── models/                 # Trained models (artifacts)
│   ├── rf_model.pkl
│   └── programas.pkl
├── docs/                   # Documentation
├── tests/                  # Tests
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🚀 Tech Stack

| Category | Technologies |
|----------|-------------|
| **Platform** | Databricks, Unity Catalog |
| **Processing** | PySpark, Spark SQL |
| **Storage** | Delta Lake, Volumes |
| **ML** | scikit-learn |
| **API** | FastAPI |
| **Inference** | joblib |
| **Testing** | pytest |

## 📝 Usage

### Running the Pipeline in Databricks

1. **Bronze Layer**
```python
from preprocessing import load_bronze, save_bronze

# Load and store raw data
df_bronze = load_bronze(spark)
save_bronze(spark, df_bronze)
```

2. **Silver Layer**
```python
from preprocessing import transform_bronze_to_silver, save_silver

# Transform and store cleaned data
df_bronze = spark.table("bronze.admissions_raw")
df_silver = transform_bronze_to_silver(df_bronze)
save_silver(spark, df_silver)
```

3. **Gold Layer**
```python
from preprocessing import transform_silver_to_gold, save_gold

# Transform and store ML features
df_silver = spark.table("silver.admissions_clean")
df_gold = transform_silver_to_gold(df_silver)
save_gold(spark, df_gold)
```

### Running the Inference API

```bash
# Run the API (consumes preprocessed data)
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Or with Docker
docker build -t admissions-api .
docker run -p 8000:8000 admissions-api
```

## 📊 Data Quality Considerations

### Bronze Layer
- Schema validation on CSV ingestion
- Handle missing values and nulls
- Record data lineage (source, timestamp)

### Silver Layer
- Feature scaling consistency
- Encoding completeness checks
- Distribution validation for numerical features

### Gold Layer
- Final schema validation before export
- Feature correlation analysis
- Target variable balance check

## 🔍 Key Data Engineering Concepts

**Medallion Architecture:**
- Progressive data quality improvement across layers
- Isolation of concerns (ingest → clean → serve)
- Independent layer maintenance and updates

**Feature Engineering:**
- Reusable transformation logic
- Versioned feature definitions
- Consistent encoding across training and inference

**Scalability:**
- PySpark handles 125K+ records efficiently
- Delta Lake provides ACID transactions
- Incremental processing capabilities

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

## 👤 Author

**Tomás Campoy Rojo**
- GitHub: [@tommcrojo](https://github.com/tommcrojo)

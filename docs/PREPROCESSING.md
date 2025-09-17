# Preprocessing Pipeline Documentation

## Overview

This document describes the data preprocessing pipeline implemented in PySpark for the university admissions dataset. The pipeline follows the medallion architecture pattern commonly used in modern data lakehouse implementations.

## Architecture

```
Raw CSV → Bronze (Raw) → Silver (Cleaned + Features) → Gold (ML-Ready)
```

## Layer Descriptions

### Bronze Layer (`bronze.admissions_raw`)

**Purpose:** Landing zone for raw data with minimal transformation.

**Characteristics:**
- Raw schema from CSV source
- Schema inference on load
- Contains all original columns
- No feature engineering applied

**Load Command:**
```python
df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("delimiter", ",") \
    .csv("/path/to/admissions_synthetic_ucam2.csv")
```

**Data Quality Checks:**
- Verify column count matches expected (12 columns)
- Check for null values in key fields (dni, nota_acceso)
- Validate data types (int for dni, double for nota_acceso)

### Silver Layer (`silver.admissions_clean`)

**Purpose:** Apply data cleaning and feature engineering transformations.

**Transformations:**

#### 1. Grade Normalization
```python
nota_normalizada = (nota_acceso - 5.0) / 5.0
```
- Input: 0-10 scale
- Output: 0-1 normalized scale
- Rationale: ML models perform better with normalized features

#### 2. High School Track One-Hot Encoding
```python
rama_ciencias = 1 if rama_bachillerato == "Ciencias" else 0
rama_sociales = 1 if rama_bachillerato == "Ciencias Sociales" else 0
rama_ingenieria = 1 if rama_bachillerato == "Ingeniería" else 0
```
- Converts categorical variable to binary features
- Enables model to learn patterns per track
- Missing/other tracks encoded as all zeros

#### 3. Geographic Indicator
```python
es_murcia = 1 if provincia == "Murcia" else 0
```
- Binary feature for regional differentiation
- Local students may have different success patterns

#### 4. Modality Indicator
```python
es_online = 1 if modalidad == "Online" else 0
```
- Distinguishes online vs in-person study
- Online students may face different challenges

#### 5. Credit Load Ratio
```python
creditos_ratio = creditos_primera_matricula / 60.0
```
- Normalizes credit load to full-time equivalent
- Values > 1.0 indicate overload
- Values < 1.0 indicate part-time enrollment

**Silver Schema:**
| Column | Type | Source/Transformation |
|--------|------|----------------------|
| dni | int | Original |
| nombre | string | Original |
| edad | int | Original |
| nota_acceso | double | Original |
| rama_bachillerato | string | Original |
| provincia | string | Original |
| es_extranjero | boolean | Original |
| modalidad | string | Original |
| programa_elegido | string | Original |
| ano_ingreso | int | Original |
| creditos_primera_matricula | int | Original |
| exito_academico | int | Original |
| **nota_normalizada** | double | (nota_acceso - 5) / 5 |
| **rama_ciencias** | int | One-hot |
| **rama_sociales** | int | One-hot |
| **rama_ingenieria** | int | One-hot |
| **es_murcia** | int | One-hot |
| **es_online** | int | One-hot |
| **creditos_ratio** | double | credits / 60 |

### Gold Layer (`gold.ml_features`)

**Purpose:** Provide final ML-ready feature set.

**Feature Selection Rationale:**
- **Identifiers:** `dni` (key), `programa_elegido` (reference)
- **Target:** `exito_academico` (binary classification)
- **Numerical:** `nota_normalizada`, `edad`, `creditos_ratio`
- **Encoded:** All binary features (rama_*, es_*, etc.)

**Gold Schema:**
| Column | Type | Purpose |
|--------|------|---------|
| dni | int | Primary key |
| programa_elegido | string | Reference only |
| exito_academico | int | Target variable (0/1) |
| nota_normalizada | double | Normalized grade |
| edad | int | Student age |
| creditos_ratio | double | Course load |
| rama_ciencias | int | Sciences track indicator |
| rama_sociales | int | Social Sciences track indicator |
| rama_ingenieria | int | Engineering track indicator |
| es_murcia | int | Regional indicator |
| es_extranjero | int | International indicator |
| es_online | int | Modality indicator |

## Usage Examples

### Running the Full Pipeline

```python
from pyspark.sql import SparkSession
from preprocessing import (
    load_bronze, save_bronze,
    transform_bronze_to_silver, save_silver,
    transform_silver_to_gold, save_gold
)

spark = SparkSession.builder.getOrCreate()

# Bronze: Load raw data
df_bronze = load_bronze(spark)
save_bronze(spark, df_bronze)

# Silver: Clean and engineer features
df_bronze = spark.table("bronze.admissions_raw")
df_silver = transform_bronze_to_silver(df_bronze)
save_silver(spark, df_silver)

# Gold: Final ML features
df_silver = spark.table("silver.admissions_clean")
df_gold = transform_silver_to_gold(df_silver)
save_gold(spark, df_gold)
```

### Exporting for ML Training

```python
# Convert to pandas for sklearn
df_pandas = spark.table("gold.ml_features").toPandas()

# Define features and target
feature_cols = [
    "nota_normalizada", "edad", "creditos_ratio",
    "rama_ciencias", "rama_sociales", "rama_ingenieria",
    "es_murcia", "es_online", "es_extranjero"
]

X = df_pandas[feature_cols]
y = df_pandas["exito_academico"]
```

## Data Lineage

```
Raw CSV
    ↓ ingest
bronze.admissions_raw
    ↓ transform
silver.admissions_clean
    ↓ select
gold.ml_features
    ↓ export
ML Training / Inference API
```

## Performance Considerations

- **Caching:** Cache intermediate DataFrames when processing multiple times
- **Partitioning:** Repartition by `programa_elegido` for model-specific queries
- **Schema Enforcement:** Use explicit schemas for production workloads

## Future Enhancements

1. **Data Quality:** Add automated data quality rules (Great Expectations)
2. **Versioning:** Implement feature versioning in gold layer
3. **Monitoring:** Add pipeline metrics and alerting
4. **Incremental:** Support incremental processing for new data

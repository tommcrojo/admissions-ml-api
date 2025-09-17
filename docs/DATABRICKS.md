# Databricks Implementation Guide

## Setup

### Required Resources

- **Databricks Workspace:** Unity Catalog enabled
- **Volumes:** Bronze storage location for CSV files
- **Compute:** At least 1 node cluster (any tier)

### Catalog Structure

```sql
-- Create catalogs and databases
CREATE CATALOG IF NOT EXISTS workspace;

CREATE DATABASE IF NOT EXISTS bronze;
CREATE DATABASE IF NOT EXISTS silver;
CREATE DATABASE IF NOT EXISTS gold;

-- Grant permissions (adjust based on your needs)
GRANT ALL PRIVILEGES ON DATABASE bronze TO users;
GRANT ALL PRIVILEGES ON DATABASE silver TO users;
GRANT ALL PRIVILEGES ON DATABASE gold TO users;
```

## Running Notebooks

### 1. Bronze Layer (00_load_data)

1. Upload CSV to Volume:
   - Navigate to Catalog → workspace → bronze
   - Create Volume: `synthetic_data`
   - Upload `admissions_synthetic_ucam2.csv`

2. Run notebook:
   ```python
   df = (spark.read
         .option("header", "true")
         .option("inferSchema", "true")
         .option("delimiter", ",")
         .csv("/Volumes/workspace/bronze/synthetic_data/admissions_synthetic_ucam2.csv"))
   
   spark.sql("CREATE DATABASE IF NOT EXISTS bronze")
   df.write.mode("overwrite").saveAsTable("bronze.admissions_raw")
   
   display(spark.table("bronze.admissions_raw"))
   ```

3. Verify:
   ```python
   # Check record count
   spark.table("bronze.admissions_raw").count()  # Expected: ~125K
   
   # Check schema
   spark.table("bronze.admissions_raw").printSchema()
   ```

### 2. Silver Layer (01_bronze_to_silver)

1. Run transformation:
   ```python
   from pyspark.sql import functions as F
   
   df_bronze = spark.table("bronze.admissions_raw")
   
   df_silver = (
       df_bronze
       .withColumn("nota_normalizada", (F.col("nota_acceso") - 5.0) / 5.0)
       .withColumn("rama_ciencias", F.when(F.col("rama_bachillerato") == "Ciencias", 1).otherwise(0))
       .withColumn("rama_sociales", F.when(F.col("rama_bachillerato") == "Ciencias Sociales", 1).otherwise(0))
       .withColumn("rama_ingenieria", F.when(F.col("rama_bachillerato") == "Ingeniería", 1).otherwise(0))
       .withColumn("es_murcia", F.when(F.col("provincia") == "Murcia", 1).otherwise(0))
       .withColumn("es_online", F.when(F.col("modalidad") == "Online", 1).otherwise(0))
       .withColumn("creditos_ratio", F.col("creditos_primera_matricula") / 60.0)
   )
   
   spark.sql("CREATE DATABASE IF NOT EXISTS silver")
   df_silver.write.mode("overwrite").saveAsTable("silver.admissions_clean")
   
   display(df_silver)
   ```

2. Verify transformations:
   ```python
   # Check normalized grades
   spark.table("silver.admissions_clean").select(
       "nota_acceso", "nota_normalizada"
   ).show(5)
   
   # Check encoding
   spark.table("silver.admissions_clean").groupBy(
       "rama_bachillerato"
   ).agg(
       F.sum("rama_ciencias").alias("ciencias"),
       F.sum("rama_sociales").alias("sociales"),
       F.sum("rama_ingenieria").alias("ingenieria")
   ).show()
   ```

### 3. Gold Layer (02_silver_to_gold)

1. Run feature selection:
   ```python
   df_gold = (
       spark.table("silver.admissions_clean")
       .select(
           "dni", "programa_elegido", "exito_academico",
           "nota_normalizada", "edad", "creditos_ratio",
           "rama_ciencias", "rama_sociales", "rama_ingenieria",
           "es_murcia", "es_extranjero", "es_online"
       )
   )
   
   spark.sql("CREATE DATABASE IF NOT EXISTS gold")
   df_gold.write.mode("overwrite").saveAsTable("gold.ml_features")
   
   display(df_gold.describe())
   ```

2. Verify ML features:
   ```python
   # Check feature distributions
   spark.table("gold.ml_features").select(
       "nota_normalizada", "edad", "creditos_ratio"
   ).summary().show()
   
   # Check class balance
   spark.table("gold.ml_features").groupBy(
       "exito_academico"
   ).count().show()
   ```

### 4. Model Training (03_train_model)

1. Export to pandas for sklearn:
   ```python
   import pandas as pd
   from sklearn.ensemble import RandomForestClassifier
   from sklearn.model_selection import train_test_split
   from sklearn.metrics import roc_auc_score
   import joblib
   
   # Load features
   df = spark.table("gold.ml_features").toPandas()
   
   # Define features
   feature_cols = [
       "nota_normalizada", "edad", "creditos_ratio",
       "rama_ciencias", "rama_sociales", "rama_ingenieria",
       "es_murcia", "es_extranjero", "es_online"
   ]
   
   X = df[feature_cols]
   y = df['exito_academico']
   
   # Split data
   X_train, X_test, y_train, y_test = train_test_split(
       X, y, test_size=0.2, random_state=42
   )
   
   # Train model
   rf = RandomForestClassifier(
       n_estimators=100, 
       max_depth=5, 
       random_state=42
   )
   rf.fit(X_train, y_train)
   
   # Evaluate
   y_pred_proba = rf.predict_proba(X_test)[:, 1]
   auc = roc_auc_score(y_test, y_pred_proba)
   print(f"AUC: {auc:.3f}")
   
   # Save model
   joblib.dump(rf, '/Volumes/workspace/gold/ml-model/rf_model.pkl')
   joblib.dump(
       df["programa_elegido"].unique().tolist(), 
       '/Volumes/workspace/gold/ml-model/programas.pkl'
   )
   ```

2. Feature importance:
   ```python
   import pandas as pd
   
   fi = pd.DataFrame({
       'feature': feature_cols,
       'importance': rf.feature_importances_
   }).sort_values('importance', ascending=False)
   
   display(fi)
   ```

## Production Considerations

### Delta Lake

Use Delta tables for ACID transactions:
```python
df.write.format("delta").mode("overwrite").saveAsTable("bronze.admissions_raw")
```

### Orchestration

Use Databricks Workflows for automated pipeline execution:
1. Create new workflow
2. Add notebook tasks in order:
   - 00_load_data
   - 01_bronze_to_silver
   - 02_silver_to_gold
   - 03_train_model
3. Schedule (daily/weekly)

### Monitoring

- Log record counts at each layer
- Monitor job runtimes
- Set up alerts for failures

### Security

- Use Unity Catalog for fine-grained access control
- Limit permissions on bronze layer (read-only for analysts)
- Grant write permissions on silver/gold for data engineers

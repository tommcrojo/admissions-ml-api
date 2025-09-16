# Databricks Notebook - Python

# Command 1
# Crear features finales para ML
df_gold = (
    spark.table("silver.admissions_clean")
    .select(
        "dni", "programa_elegido", "exito_academico",
        "nota_normalizada", "edad", "creditos_ratio",
        "rama_ciencias", "rama_sociales", "rama_ingenieria",
        "es_murcia", "es_extranjero", "es_online"
    )
)

# Command 2
spark.sql("CREATE DATABASE IF NOT EXISTS gold")
df_gold.write.mode("overwrite").saveAsTable("gold.ml_features")

# Command 3
# Estadísticas básicas
display(df_gold.describe())


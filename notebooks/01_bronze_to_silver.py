# Databricks Notebook - Python

# Command 1
display(df_silver)

# Command 2
# Guardar
spark.sql("CREATE DATABASE IF NOT EXISTS silver")
df_silver.write.mode("overwrite").saveAsTable("silver.admissions_clean")


# Command 3
# Feature engineering
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


# Command 4
# Leer bronze
df_bronze = spark.table("bronze.admissions_raw")

# Command 5
from pyspark.sql import functions as F


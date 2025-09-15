"""Silver layer: Data cleaning and feature engineering.

This module transforms raw bronze data into clean, feature-enriched
silver layer data with standardized transformations.
"""

from pyspark.sql import DataFrame, functions as F


def transform_bronze_to_silver(df_bronze: DataFrame) -> DataFrame:
    """Transform bronze layer to silver layer with feature engineering.

    Transformations applied:
    - nota_normalizada: Normalize grades from 0-10 scale to 0-1
    - rama_*: One-hot encode high school track (Ciencias/Sociales/Ingeniería)
    - es_murcia: Binary indicator for Murcia province
    - es_online: Binary indicator for online modality
    - creditos_ratio: Ratio of credits to standard 60-credit full load

    Args:
        df_bronze: Raw data from bronze.admissions_raw

    Returns:
        DataFrame with engineered features for silver.admissions_clean

    Example:
        >>> df_silver = transform_bronze_to_silver(df_bronze)
        >>> spark.sql("CREATE DATABASE IF NOT EXISTS silver")
        >>> df_silver.write.mode("overwrite").saveAsTable("silver.admissions_clean")
    """
    df_silver = (
        df_bronze.withColumn("nota_normalizada", (F.col("nota_acceso") - 5.0) / 5.0)
        .withColumn(
            "rama_ciencias",
            F.when(F.col("rama_bachillerato") == "Ciencias", 1).otherwise(0),
        )
        .withColumn(
            "rama_sociales",
            F.when(F.col("rama_bachillerato") == "Ciencias Sociales", 1).otherwise(0),
        )
        .withColumn(
            "rama_ingenieria",
            F.when(F.col("rama_bachillerato") == "Ingeniería", 1).otherwise(0),
        )
        .withColumn("es_murcia", F.when(F.col("provincia") == "Murcia", 1).otherwise(0))
        .withColumn("es_online", F.when(F.col("modalidad") == "Online", 1).otherwise(0))
        .withColumn("creditos_ratio", F.col("creditos_primera_matricula") / 60.0)
    )

    return df_silver


def save_silver(spark, df: DataFrame) -> None:
    """Save DataFrame to silver layer table.

    Args:
        spark: Active SparkSession
        df: DataFrame to save
    """
    spark.sql("CREATE DATABASE IF NOT EXISTS silver")
    df.write.mode("overwrite").saveAsTable("silver.admissions_clean")

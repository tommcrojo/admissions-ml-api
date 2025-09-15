"""Gold layer: Final ML-ready feature selection.

This module prepares the gold layer with final features
optimized for machine learning model training.
"""

from pyspark.sql import DataFrame


def transform_silver_to_gold(df_silver: DataFrame) -> DataFrame:
    """Transform silver layer to gold layer with ML-ready features.

    Selected features for model training:
    - dni: Student identifier
    - programa_elegido: Chosen academic program (for reference)
    - exito_academico: Target variable (0/1)
    - nota_normalizada: Normalized access grade (0-1)
    - edad: Student age
    - creditos_ratio: Credits ratio relative to standard load
    - rama_ciencias: One-hot for Sciences track
    - rama_sociales: One-hot for Social Sciences track
    - rama_ingenieria: One-hot for Engineering track
    - es_murcia: Murcia province indicator
    - es_extranjero: International student indicator
    - es_online: Online modality indicator

    Args:
        df_silver: Cleaned data from silver.admissions_clean

    Returns:
        DataFrame with final features for gold.ml_features

    Example:
        >>> df_gold = transform_silver_to_gold(df_silver)
        >>> spark.sql("CREATE DATABASE IF NOT EXISTS gold")
        >>> df_gold.write.mode("overwrite").saveAsTable("gold.ml_features")
    """
    df_gold = df_silver.select(
        "dni",
        "programa_elegido",
        "exito_academico",
        "nota_normalizada",
        "edad",
        "creditos_ratio",
        "rama_ciencias",
        "rama_sociales",
        "rama_ingenieria",
        "es_murcia",
        "es_extranjero",
        "es_online",
    )

    return df_gold


def save_gold(spark, df: DataFrame) -> None:
    """Save DataFrame to gold layer table.

    Args:
        spark: Active SparkSession
        df: DataFrame to save
    """
    spark.sql("CREATE DATABASE IF NOT EXISTS gold")
    df.write.mode("overwrite").saveAsTable("gold.ml_features")

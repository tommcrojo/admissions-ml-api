"""Bronze layer: Raw data ingestion and storage.

This module handles loading raw CSV data into the bronze layer
in the Databricks Unity Catalog lakehouse.
"""

from pyspark.sql import DataFrame, SparkSession


def load_bronze(
    spark: SparkSession,
    csv_path: str = "/Volumes/workspace/bronze/synthetic_data/admissions_synthetic_ucam2.csv",
) -> DataFrame:
    """Load raw CSV data into bronze layer.

    Args:
        spark: Active SparkSession
        csv_path: Path to raw CSV file in Databricks Volumes

    Returns:
        DataFrame with raw admissions data

    Example:
        >>> df_bronze = load_bronze(spark)
        >>> spark.sql("CREATE DATABASE IF NOT EXISTS bronze")
        >>> df_bronze.write.mode("overwrite").saveAsTable("bronze.admissions_raw")
    """
    df = (
        spark.read.option("header", "true")
        .option("inferSchema", "true")
        .option("delimiter", ",")
        .csv(csv_path)
    )

    return df


def save_bronze(spark: SparkSession, df: DataFrame) -> None:
    """Save DataFrame to bronze layer table.

    Args:
        spark: Active SparkSession
        df: DataFrame to save
    """
    spark.sql("CREATE DATABASE IF NOT EXISTS bronze")
    df.write.mode("overwrite").saveAsTable("bronze.admissions_raw")

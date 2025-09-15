"""Preprocessing pipeline for university admissions data.

This module contains PySpark transformations for the medallion architecture:
- Bronze: Raw data ingestion
- Silver: Cleaning and feature engineering
- Gold: Final ML-ready features
"""

from .bronze import load_bronze
from .silver import transform_bronze_to_silver
from .gold import transform_silver_to_gold

__all__ = ["load_bronze", "transform_bronze_to_silver", "transform_silver_to_gold"]

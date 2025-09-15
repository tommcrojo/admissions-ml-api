"""Utility functions for data preprocessing pipeline."""

from pyspark.sql import DataFrame


def display_data_summary(df: DataFrame, description: str = "") -> None:
    """Display summary statistics for a DataFrame.

    Args:
        df: DataFrame to summarize
        description: Optional description to display
    """
    if description:
        print(f"\n{'=' * 60}")
        print(f"{description}")
        print("=" * 60)

    print(f"\nSchema:")
    df.printSchema()

    print(f"\nCount: {df.count()}")

    print(f"\nSummary statistics:")
    df.describe().show()

import logging
from typing import Any

import polars as pl

from config import enable_debug_logs

logger = logging.getLogger(__name__)
DEBUG_MODE = logger.isEnabledFor(logging.DEBUG)


def sort_columns (df: pl.LazyFrame) -> pl.LazyFrame:
    """Sorts and reorders columns.

    Args:
        df (pl.LazyFrame): Post-transformation query plan (LazyFrame).

    Returns:
        pl.LazyFrame: Query plan (LazyFrame).
    """
    
    # Apply schema to reorder columns
    df = df.match_to_schema({
        "report": pl.String,
        "region": pl.String, 
        "weaponcategory": pl.String, 
        "date": pl.Datetime("us")
    })

    df = df.sort(by=["date", "region"], descending=False)

    df = df.drop_nulls()

    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE)
    
    return df


def export_data(df: pl.LazyFrame, processed_path: str, config: dict[str, Any]) -> None:
    """Exports data to gzip compressed parquet file.

    Args:
        df (pl.LazyFrame): Query plan (LazyFrame) with sorted and reordered columns.
        processed_path: File path to which the data should be wrtitten.
        config (dict): YAML configuration dictionary.
    """

    # Write data to compressed parquet file
    df.sink_parquet(
        path=processed_path,
        compression=config["settings"]["parquet_compression"]
    )
    logger.info(f"Exported data to '{processed_path}'.")

    return None
import logging

import polars as pl
import polars.selectors as cs

from config import enable_debug_logs

logger = logging.getLogger(__name__)
DEBUG_MODE = logger.isEnabledFor(logging.DEBUG)


def import_json(raw_path: str) -> pl.LazyFrame:
    """Imports JSON data into Polars LazyFrame.

    Args:
        raw_path (str): Path to the raw JSON file.

    Returns:
        pl.LazyFrame: Query plan (LazyFrame).
    """

    df = pl.read_json(raw_path)

    # Generate info logs
    enable_debug_logs(df, is_debug=True)
    logger.debug(f"Estimated Size: {df.estimated_size('mb'):.0f} MB")

    return df.lazy()


def drop_duplicates(df: pl.LazyFrame) -> pl.LazyFrame:
    """Drops duplicate records before filtering columns.

    Args:
        df (pl.LazyFrame): Import query plan (LazyFrame).

    Returns:
        pl.LazyFrame: Query plan (LazyFrame).
    """

    df = df.unique(maintain_order=False, keep="any")

    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE)

    return df


def select_columns(df: pl.LazyFrame) -> pl.LazyFrame:
    """Selects columns from the available dataset.

    Args:
        df (pl.LazyFrame): Query plan (LazyFrame) with no duplicates.

    Returns:
        pl.LazyFrame: Query plan (LazyFrame).
    """

    columns = ["weaponkind","organunit","reasonsearch","insertdate","theftdate"]
    df = df.select(columns)

    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE)

    return df


def cast_dtypes(df: pl.LazyFrame) -> pl.LazyFrame:
    """Casts correct data types onto columns.

    Args:
        df (pl.LazyFrame): Query plan (LazyFrame) with selected columns.

    Returns:
        pl.LazyFrame: Query plan (LazyFrame).
    """

    df = df.with_columns(
        pl.col("weaponkind").cast(pl.String),
        pl.col("organunit").cast(pl.String),
        pl.col("reasonsearch").cast(pl.String),
        pl.col("insertdate").str.strptime(pl.Datetime("us"), "%Y-%m-%dT%H:%M:%S"),
        pl.col("theftdate").str.strptime(pl.Datetime("us"), "%Y-%m-%dT%H:%M:%S")
    )

    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE)

    return df


def drop_nulls(df: pl.LazyFrame) -> pl.LazyFrame:
    """Removes rows using the following sequence of operations:
    1) drops rows full of null values; 
    2) drops rows with at least one string value missing; 
    3) drops rows with both datetime values missing.

    Args:
        df (pl.LazyFrame): Query plan (LazyFrame) with correct data types.

    Returns:
        pl.LazyFrame: Query plan (LazyFrame).
    """

    # Drop rows consisting of nulls only
    df = df.filter(~pl.all_horizontal(pl.all().is_null()))
    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE, name="Dropped rows full of nulls.")

    # Drop rows where any string values are missing
    df = df.drop_nulls(subset=cs.string())
    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE, name="Dropped rows with any string values missing.")

    # Drop rows were both datetime columns contain nulls
    df = df.filter(~(pl.col("insertdate").is_null() & pl.col("theftdate").is_null()))
    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE, name="Dropped rows with both datetime values missing.")

    return df
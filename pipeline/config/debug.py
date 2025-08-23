import os
import yaml
import logging
from typing import Any

import polars as pl

logger = logging.getLogger(__name__)
DEBUG_MODE = logger.isEnabledFor(logging.DEBUG)


def load_config() -> dict[str, Any] | Any:
    """Load configurations from YAML file relative to this file."""
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def enable_debug_logs(
        df: pl.LazyFrame | pl.DataFrame,
        is_debug: bool = DEBUG_MODE,
        name: None | str = None
    ) -> None:
    """This function is used to display detailed information about dataset
    that the function outside currently uses.

    Allows to set custom name for easier logs navigation.
    
    It materializes LazyFrame and computes info only if logger level is DEBUG, 
    which is represented by 'is_debug' parameter.

    Warning: It is computationaly heavy and should be used with caution. 

    Args:
        df (pl.LazyFrame): Query plan (LazyFrame) to use for dataset info extraction.
        is_debug (bool, optional): Boolean representing whether logger level is set to debug.
            Defaults to DEBUG_MODE.
    """

    if is_debug:
        if isinstance(df, pl.LazyFrame):
            # Get number of rows in a LazyFrame
            rows: int = (
                df
                .select(pl.len())
                .collect()
                .item()
            )
            # Generate a dataframe with a number of null values for each column
            nulls: list[tuple[str,int]] = (
                df
                .null_count()
                .unpivot(variable_name='column', value_name='total_nulls')
                .select(['column', 'total_nulls'])
                .collect()
                .rows()
            )
            # Generate a dataframe sample of the first record (dtypes included)
            first: pl.DataFrame = df.head(1).collect()
            # Generate a dataframe sample of the last record (dtypes included)
            last: pl.DataFrame = df.tail(1).collect()

        elif isinstance(df, pl.DataFrame):
            # Get number of rows in a DataFrame
            rows = (
                df
                .select(pl.len())
                .item()
            )
            # Generate a dataframe with a number of null values for each column
            nulls = (
                df
                .null_count()
                .unpivot(variable_name='column', value_name='total_nulls')
                .select(['column', 'total_nulls'])
                .rows()
            )
            # Generate a dataframe sample of the first record (dtypes included)
            first = df.head(1)
            # Generate a dataframe sample of the last record (dtypes included)
            last = df.tail(1)

        else:
            return None
        
        if isinstance(name, str):
            logger.debug(name)
        logger.debug(f"Rows: {rows:,}")
        logger.debug(f"Nulls: {nulls}")
        logger.debug(f"Sample (First): {first}")
        logger.debug(f"Sample (Last): {last}")

    return None
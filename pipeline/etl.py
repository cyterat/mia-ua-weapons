import os
import sys
import logging
from typing import Any

import polars as pl

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from config import load_config # noqa: E402

# Load config
config: dict[str, Any] = load_config()
log_level: str = getattr(logging, config["settings"]["log_level"])
export_logs: bool = config["settings"]["export_logs"]

# Conditional debug logs export (config.yaml)
file_name = None
encoding = None
file_mode = "a"
if export_logs:
    file_name = os.path.join(*config["files"]["etl_logs_path"])
    file_mode = "w" 
    encoding = "utf-8"

# Configure logging globally
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=file_name,
    filemode=file_mode,
    encoding=encoding,
    force=True
)

from etl import extract, transform, load # noqa: E402

logger = logging.getLogger(__name__)
DEBUG_MODE = logger.isEnabledFor(logging.DEBUG)


def run_extraction(config: dict[str, Any]) -> pl.LazyFrame:
    logger.info("Beginning data extraction...")
    raw_path = os.path.join(*config["files"]["raw_path"])

    logger.info("1/5 Importing data...")
    df = extract.import_json(raw_path)

    logger.info("2/5 Dropping duplicates...")
    df = extract.drop_duplicates(df)

    logger.info("3/5 Selecting columns...")
    df = extract.select_columns(df)

    logger.info("4/5 Casting datatypes...")
    df = extract.cast_dtypes(df)

    logger.info("5/5 Dropping nulls...")
    df = extract.drop_nulls(df)

    return df


def run_transforms(df: pl.LazyFrame, config: dict[str, Any]) -> pl.LazyFrame:
    logger.info("Beginning data transformation...")

    logger.info("1/4 Transforming 'reasonsearch' column...")
    df = transform.transform_column_reasonsearch(df)

    logger.info("2/4 Transforming 'organunit' column...")
    df = transform.transform_column_organunit(df, config)

    logger.info("3/4 Transforming 'weaponkind' column...")
    df, wps_df = transform.transform_column_weaponkind(df, config)
    df = transform.check_new_weapons(df, wps_df)

    logger.info("4/4 Transforming date columns...")
    df = transform.transform_column_dates(df)

    return df


def run_load(df: pl.LazyFrame, config: dict[str, Any]) -> None:
    logger.info("Beginning data loading...")
    processed_path = os.path.join(*config["files"]["processed_path"])

    logger.info("1/2 Sorting columns...")
    df = load.sort_columns(df)

    logger.info("2/2 Exporting data...")
    load.export_data(df, processed_path, config)


def main() -> None:
    try:  
        df = run_extraction(config)
        df = run_transforms(df, config)
        run_load(df, config)

        logging.info("Pipeline run was successful.")

    except Exception as e:
        logging.critical(f"Pipeline run failed: {e.__class__.__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
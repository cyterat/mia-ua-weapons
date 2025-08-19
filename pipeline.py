import os
import sys
import yaml
import logging
from datetime import datetime

import polars as pl
import polars.selectors as cs


def load_config() -> dict:
    """Load configurations from YAML file."""
    config_path = os.path.join("config.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
    
config = load_config()

# Set up logging
log_level = getattr(logging, config["settings"]["log_level"])
logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s', filename='debug.log', encoding='utf-8')

logger = logging.getLogger(__name__)
DEBUG_MODE = logger.isEnabledFor(logging.DEBUG)

INPUT_PATH = os.path.join(
    config["files"]["input_dir"],
    config["files"]["input_file"]
)
OUTPUT_PATH = os.path.join(
    config["files"]["output_dir"],
    config["files"]["output_file"]
)


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

###############################################################
                    # SCRIPT SPLIT HERE
###############################################################

def import_json(input_path: str = INPUT_PATH) -> pl.LazyFrame:
    """Imports JSON data into Polars LazyFrame.

    Returns:
        pl.LazyFrame: Query plan (LazyFrame).
    """

    df = pl.read_json(input_path)

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

###############################################################
                    # SCRIPT SPLIT HERE
###############################################################

def transform_column_reasonsearch(df: pl.LazyFrame) -> pl.LazyFrame:
    """Replaces UKR names of report types with ENG ones. Creates column 'report'.

    Args:
        df (pl.LazyFrame): Post-extraction query plan (LazyFrame).

    Returns:
        pl.DataFrame: Query plan (LazyFrame).
    """

    # Replace/translate report types to English
    df = df.with_columns(
        pl.col("reasonsearch").str.replace_many({"ВИКРАДЕННЯ":"Theft", "ВТРАТА":"Loss"})
        .alias("reasonsearch")
    )

    df = df.rename({"reasonsearch":"report"})

    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE)

    return df


def transform_column_organunit(df: pl.LazyFrame) -> pl.LazyFrame:
    """Replaces long MIA unit names with region names using regex. Creates column 'region'.

    Args:
        df (pl.LazyFrame): Post-extraction query plan (LazyFrame).

    Returns:
        pl.LazyFrame: Query plan (LazyFrame).
    """

    # [FIX] Dictionary with oblasts names (keys) and their respective regular expressions (values)
    regex_oblasts = config["regex_mappings"]["oblasts"]
    # [FIX] Dictionary with administrative centers' names (keys) and their respective regular expressions (values)
    regex_acenters = config["regex_mappings"]["adjustments"]

    # Preserve original column
    region_col = pl.col("organunit")
    
    # Apply first dictionary
    for name, regex in regex_oblasts.items():
        region_col = pl.when(
            pl.col("organunit").str.contains(regex)
        ).then(pl.lit(name)).otherwise(region_col)
    
    # Apply second dictionary (adjustments)
    for name, regex in regex_acenters.items():
        region_col = pl.when(
            pl.col("organunit").str.contains(regex)
        ).then(pl.lit(name)).otherwise(region_col)
    
    # Store combined nested expression tree in a new column
    df = df.with_columns(region_col.alias("region"))
    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE, name="Added new region column.")

    # Drop redundant column
    df = df.drop("organunit")
    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE)

    return df


def transform_column_weaponkind(df: pl.LazyFrame) -> tuple[pl.LazyFrame, pl.LazyFrame]:
    """Creates a new column with broader weapon categories. Creates column 'weaponcategory'.

    Args:
        df (pl.LazyFrame): Post-extraction query plan (LazyFrame).

    Returns:
        tuple[pl.LazyFrame, pl.LazyFrame]: Lazy query plans for data with original weapon names and additional weapon mappings.
    """
    
    # [FIX] Temporary Series objects below will be later used to populate a DataFrame
    bladed = pl.LazyFrame(
        data=config["weapon_mappings"]["bladed"],
        schema={"Bladed":pl.String}
    )
    handguns = pl.LazyFrame(
        data=config["weapon_mappings"]["handguns"],
        schema={"Handguns":pl.String}
    )
    lfirearms = pl.LazyFrame(
        data=config["weapon_mappings"]["lfirearms"],
        schema={"Light firearms":pl.String}
    )
    hfirearms = pl.LazyFrame(
        data=config["weapon_mappings"]["hfirearms"],
        schema={"Heavy firearms":pl.String}
    )
    pneumaticflob = pl.LazyFrame(
        data=config["weapon_mappings"]["pneumaticflob"],
        schema={"Pneumatic&Flobert":pl.String}
    )
    artillery = pl.LazyFrame(
        data=config["weapon_mappings"]["artillery"],
        schema={"Artillery":pl.String}
    )
    explosives = pl.LazyFrame(
        data=config["weapon_mappings"]["explosives"],
        schema={"Explosives":pl.String}
    )
    other = pl.LazyFrame(
        data=config["weapon_mappings"]["other"],
        schema={"Other":pl.String}
    )

    # Concatenate LazyFrames into a single one
    wps_df = pl.concat(
        [bladed, handguns, lfirearms, hfirearms, pneumaticflob, artillery, explosives, other],
        how="horizontal"
    )
    
    # Unpivot LazyFrame (columns to rows)
    wps_df = wps_df.unpivot(variable_name="weaponcategory", value_name="weaponkind").drop_nulls()

    # Join weapon names with matching weapon categories 
    df = df.join(other=wps_df, on="weaponkind", how="left")

    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE)

    return df, wps_df 


def check_new_weapons(df: pl.LazyFrame, wps_df: pl.LazyFrame) -> pl.LazyFrame:
    """Checks for new weapons, drops nulls redundant 'weaponkind' column,
    and removes rows with missing weapon categories.

    Args:
        df (pl.LazyFrame): Query plan (LazyFrame) with original weapon names.
        wps_df (pl.LazyFrame): Query plan (LazyFrame) with additional weapon mappings.

    Returns:
        pl.LazyFrame: Query plan (LazyFrame).
    """

    # Check wether any new weapons are present in a dataset
    has_null = df.select(pl.col("weaponcategory").is_null().any()).collect().item()
    if has_null:

        new_weapons = set()
        count = 0

        # Store weaponkind values that don't have respective weaponcategory value
        wep_list = (
            df
            .filter(pl.col("weaponcategory").is_null())
            .select("weaponkind")
            .collect()
            .get_column("weaponkind")
            .to_list()
        )

        # Iterate over list of (new) weapons to check if those values are present in current wps_df dataset
        for w in wep_list: 
            if w not in wps_df.collect().get_column("weaponkind"):
                new_weapons.add(w)
                count += 1

        logger.warning(f"{count} records of {len(new_weapons)} new weapons present: {str(new_weapons)[1:-1]}.\nUpdate weapon_mappings in config.yaml with new weapons!")
    else:
        logger.info("No records with new weapons found.")

    # Drop redundant column
    df = df.drop("weaponkind")
    # Drop all rows that contain any nulls
    df = df.drop_nulls()

    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE)

    return df
    

def transform_column_dates(df: pl.LazyFrame) -> pl.LazyFrame:
    """Creates a new date column using/replacing 'theftdate' and 'insertdate'.
    Removes and substitutes records preserving historical accuracy during post-independence period.

    Args:
        df (pl.LazyFrame): Post-extraction query plan (LazyFrame).

    Returns:
        pl.LazyFrame: Query plan (LazyFrame).
    """

    # Substitute missing values in theftdate with those from the insertdate column
    df = df.with_columns(pl.coalesce(["theftdate","insertdate"]).alias("date"))
    # Drop redundant date columns
    df = df.drop("insertdate","theftdate")

    def drop_old_rec(df: pl.LazyFrame) -> pl.LazyFrame:
        """Excludes Ukrainian SSR records from DataFrame."""
        # Store date of UKR independence
        dt_independence = datetime(year=1991, month=8, day=24)
        # Filter out pre-independence records
        df = (
            df
            .filter(pl.col("date") >= dt_independence)
            .sort(by="date", descending=False)
        )
        return df
    
    def combine_crimean_upd(df: pl.LazyFrame) -> pl.LazyFrame:
        """Applies modifications to Crimean records."""
        # Store date of de-facto lost control over records
        last_dt_crimea = datetime(year=2014, month=3, day=24)
        # Store filters
        crimea_condition = (pl.col("region") == "Simferopol") & (pl.col("date") > last_dt_crimea)
        # Preserve reference column
        date_col = pl.col("date")
        # Create expression with date replacement logic
        date_col = (
            pl.when(crimea_condition)
            .then(pl.lit(last_dt_crimea))
            .otherwise(date_col)
            .alias("date")
        )
        # Apply transformation using expression  
        df =  df.with_columns(date_col)
        return df
    
    df = drop_old_rec(df)
    df = combine_crimean_upd(df)

    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE)

    return df

###############################################################
                    # SCRIPT SPLIT HERE
###############################################################

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

    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE)
    
    return df


def export_data(df: pl.LazyFrame, output_path: str) -> None:
    """Exports data to gzip compressed parquet file.

    Args:
        df (pl.LazyFrame): Query plan (LazyFrame) with sorted and reordered columns.
        output_path: File path to which the data should be wrtitten.
    """

    # Write data to compressed parquet file
    df.sink_parquet(
        path=output_path,
        compression=config["settings"]["parquet_compression"]
    )
    logger.info(f"Exported data to {output_path}.")

    return None


if __name__ == "__main__":

    try:
        logger.info("1/5 Importing data...")
        df = import_json()

        logger.info("2/5 Dropping duplicate rows...")
        df = drop_duplicates(df)

        logger.info("3/5 Selecting required columns...")
        df = select_columns(df)

        logger.info("4/5 Casting datatypes...")
        df = cast_dtypes(df)

        logger.info("5/5 Dropping rows with missing values...")
        df = drop_nulls(df)

###############################################################
                    # SCRIPT SPLIT HERE
###############################################################

        logger.info("1/4 Transform 'reasonsearch' column...")
        df = transform_column_reasonsearch(df)
        
        logger.info("2/4 Transform 'organunit' column...")
        df = transform_column_organunit(df)

        logger.info("3/4 Transform 'weaponkind' column...")
        df, wps_df = transform_column_weaponkind(df)
        df = check_new_weapons(df, wps_df)

        logger.info("4/4 Transform date columns...")
        df = transform_column_dates(df)

###############################################################
                    # SCRIPT SPLIT HERE
###############################################################
        
        logger.info("1/2 Sort columns...")
        df = sort_columns(df)

        logger.info("2/2 Export data...")
        export_data(df, OUTPUT_PATH)

        logger.info("Pipeline run was successful.")

    except Exception as e:
        logger.critical(f"Pipeline run has failed. {e.__class__.__name__}: {e}")
        sys.exit(1)
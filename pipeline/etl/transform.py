import logging
from typing import Any
from datetime import datetime

import polars as pl

from config import enable_debug_logs

logger = logging.getLogger(__name__)
DEBUG_MODE = logger.isEnabledFor(logging.DEBUG)


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


def transform_column_organunit(df: pl.LazyFrame, config: dict[str, Any]) -> pl.LazyFrame:
    """Replaces long MIA unit names with region names using regex. Creates column 'region'.

    Args:
        df (pl.LazyFrame): Post-extraction query plan (LazyFrame).
        config (dict): YAML configuration dictionary.

    Returns:
        pl.LazyFrame: Query plan (LazyFrame).
    """

    # Dictionary with oblasts names (keys) and their respective regular expressions (values)
    regex_oblasts = config["regex_mappings"]["oblasts"]
    # Dictionary with administrative centers' names (keys) and their respective regular expressions (values)
    regex_acenters = config["regex_mappings"]["adjustments"]

    # Placeholder column with nulls
    df = df.with_columns(pl.lit(None).alias("region"))

    # Apply first set of mappings (order matters)
    for name, regex in regex_oblasts.items():
        df = df.with_columns(
            pl.when(pl.col("region").is_null() & pl.col("organunit").str.contains(regex))
            .then(pl.lit(name))
            .otherwise(pl.col("region"))
            .alias("region")
        )

    # Apply second set of mappings (order matters)
    for name, regex in regex_acenters.items():
        df = df.with_columns(
            pl.when(pl.col("region").is_null() & pl.col("organunit").str.contains(regex))
            .then(pl.lit(name))
            .otherwise(pl.col("region"))
            .alias("region")
        )
    
    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE, name="Added new region column.")

    # Drop redundant column
    df = df.drop("organunit")

    # Removing ambiguous records from the DataFrame
    df = df.filter(~pl.col("region").is_null())

    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE)

    return df


def transform_column_weaponkind(df: pl.LazyFrame, config: dict[str, Any]) -> tuple[pl.LazyFrame, pl.LazyFrame]:
    """Creates a new column with broader weapon categories. Creates column 'weaponcategory'.

    Args:
        df (pl.LazyFrame): Post-extraction query plan (LazyFrame).
        config (dict): YAML configuration dictionary.

    Returns:
        tuple[pl.LazyFrame, pl.LazyFrame]: Lazy query plans for data with original weapon names and additional weapon mappings.
    """
    
    # Temporary Series objects below will be later used to populate a DataFrame
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

    # Concatenate (hstack) LazyFrames into a single one
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

        logger.warning(
            f"""Update weapon_mappings in config.yaml with new weapons!
{count} records of {len(new_weapons)} new weapons present: {str(new_weapons)[1:-1]}."""
        )
    else:
        logger.info("No records with new weapons found.")

    # Drop redundant column
    df = df.drop("weaponkind")

    # Drop all rows that contain null in 'weaponcategory'
    df = df.drop_nulls(subset="weaponcategory")

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

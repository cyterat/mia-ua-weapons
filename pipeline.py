import os
import sys
import logging
from datetime import datetime

import pandas as pd
import polars as pl
import polars.selectors as cs
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# CURRENT_DATE = datetime.now()
FILE_PATH = os.path.join("assets","weapons-wanted.json")
OUTPUT_PATH = os.path.join("assets","ua-mia-weapons.parquet.gzip")


def import_json() -> pl.LazyFrame:
    """Imports JSON data into Polars LazyFrame.

    Returns:
        pl.LazyFrame: query plan (LazyFrame).
    """

    try:
        df = pl.read_json(FILE_PATH)

        # Materialize and compute data info only if logger level is DEBUG
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Rows: {df.height:,}")
            logger.debug(f"Columns: {df.width}")
            logger.debug(f"Estimated Size: {df.estimated_size('mb'):.0f} MB")
            logger.debug(f"Schema: {df.collect_schema()}")
            logger.debug(f"Nulls: {df.null_count().unpivot(variable_name='column',value_name='total_nulls').select(['column', 'total_nulls']).rows()}")
            logger.debug(f"Sample: {df.select(['weaponkind', 'organunit', 'reasonsearch', 'insertdate', 'theftdate']).head(1)}")

        return df.lazy()

    except FileNotFoundError:
        logger.error(f"JSON artifact not found at {FILE_PATH}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in import_json: {e.__class__.__name__}: {e}")
        sys.exit(1)


def drop_duplicates(df: pl.LazyFrame) -> pl.LazyFrame:
    """Drops duplicate records before filtering columns.

    Args:
        df (pl.LazyFrame): Imported lazy dataframe.

    Returns:
        pl.LazyFrame: Query plan (LazyFrame).
    """
    try:
        df = df.unique(maintain_order=False, keep="any")

        # Materialize and compute data info only if logger level is DEBUG
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Rows: {df.select(pl.len()).collect().item():,}")

        return df

    except Exception as e:
        logger.error(f"Unexpected error in drop_duplicates: {e.__class__.__name__}: {e}")
        sys.exit(1)


def select_columns(df: pl.LazyFrame) -> pl.LazyFrame:

    try:
        columns = ["weaponkind","organunit","reasonsearch","insertdate","theftdate"]  # Could be from config
        return df.select(columns)

    except pl.ColumnNotFoundError as e:
        logger.error(f"Required column missing: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in select_columns: {e}")
        sys.exit(1)


def cast_dtypes(df: pl.LazyFrame) -> pl.LazyFrame:

    try:
        df = df.with_columns(
            pl.col("weaponkind").cast(pl.String),
            pl.col("organunit").cast(pl.String),
            pl.col("reasonsearch").cast(pl.String),
            pl.col("insertdate").str.strptime(pl.Datetime("us"), "%Y-%m-%dT%H:%M:%S"),
            pl.col("theftdate").str.strptime(pl.Datetime("us"), "%Y-%m-%dT%H:%M:%S")
        )

        # Materialize and compute data info only if logger level is DEBUG
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Rows: {df.select(pl.len()).collect().item():,}")
            logger.debug(f"Schema: {df.collect_schema()}")

        return df

    except pl.ComputeError as e:
        logger.error(f"Type casting failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in cast_dtypes: {e}")
        sys.exit(1)


def drop_nulls(df: pl.LazyFrame) -> pl.LazyFrame:

    try:
        # Drop rows consisting of nulls only
        df = df.filter(~pl.all_horizontal(pl.all().is_null()))
        # Materialize and compute data info only if logger level is DEBUG
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Rows after removal of records full of nulls: {df.select(pl.len()).collect().item():,}")

        # Drop rows where any string values are missing
        df = df.drop_nulls(subset=cs.alpha())
        # Materialize and compute data info only if logger level is DEBUG
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Rows after removal of records with missing string values: {df.select(pl.len()).collect().item():,}")

        # Drop rows were both datetime columns contain nulls
        df = df.filter((pl.col("insertdate").is_not_null() & pl.col("theftdate").is_not_null()))
        # Materialize and compute data info only if logger level is DEBUG
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Rows after removal of records with both datetime values missing: {df.select(pl.len()).collect().item():,}")

        return df
    
    except pl.ColumnNotFoundError as e:
        logger.error(f"Required column missing: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in drop_nulls: {e}")
        sys.exit(1)


###############################################################
                    # SCRIPT SPLIT HERE
###############################################################

def transform_column_reasonsearch(df: pl.LazyFrame) -> pl.LazyFrame:
    """Replaces UKR names of report types with ENG ones. Creates column 'report'.

    Args:
        df (pl.LazyFrame): Post-extraction data.

    Returns:
        pl.DataFrame: Query plan (LazyFrame).
    """
    try:
        # Replace/translate report types to English
        df = df.with_columns(
            pl.col("reasonsearch").str.replace_many({"ВИКРАДЕННЯ":"Theft", "ВТРАТА":"Loss"})
            .alias("reasonsearch")
        )

        df = df.rename({"reasonsearch":"report"})

        # Materialize and compute data info only if logger level is DEBUG
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Rows: {df.select(pl.len()).collect().item():,}")
            logger.debug(f"Schema: {df.collect_schema()}")
            logger.debug(f"Sample: {df.head(1).collect()}")

        return df
    
    except pl.ColumnNotFoundError as e:
        logger.error(f"Required column missing: {e}")
        sys.exit(1)
    except pl.ShapeError as e:
        logger.error(f"Replacement patterns and replacement values provided to replace_many() do not match in length: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in transform_column_reasonsearch: {e}")
        sys.exit(1)


def transform_column_region(df: pl.LazyFrame) -> pl.LazyFrame:
    """Replaces long MIA unit names with region names using regex. Creates column 'region'.

    Args:
        df (pl.LazyFrame): Post-extraction data.

    Returns:
        pl.LazyFrame: Query plan (LazyFrame).
    """
    # Dictionary with oblasts names (keys) and their respective regular expressions (values)
    regex_oblasts = {
        "Uzhhorod": r"(?i)\bЗАКАРПАТ\w{0,6}.{1,5}\bобл",
        "Lviv": r"(?i)\bЛЬВ[іо]ВС\w{0,1}К\w{0,6}.{1,5}\bобл",
        "Ivano-Frankivsk": r"(?i)\b[іи]В\w{0,3}[.\-]ФР\w{0,10}.{1,5}\bобл",
        "Chernivtsi": r"(?i)\bЧЕРН[іо]В\w{0,1}Ц\w{0,6}.{1,5}\bобл",
        "Ternopil": r"(?i)\bТЕРНОП[іо]ЛЬС\w{0,6}.{1,5}\bобл",
        "Lutsk": r"(?i)\bВОЛ\w{1,2}Н\w{0,6}.{1,5}\bобл",
        "Rivne": r"(?i)\bР[іо]ВНЕНС\w{0,6}.{1,5}\bобл",
        "Zhytomyr": r"(?i)\bЖИТОМИРС\w{0,6}.{1,5}\bобл",
        "Khmelnytskyi": r"(?i)\bХМЕЛЬНИЦ\w{0,6}.{1,5}\bобл",
        "Vinnytsia": r"(?i)\bВ[іи]ННИЦ\w{0,6}.{1,5}\bобл",
        "Kyiv": r"(?i)\bКИ[їе]В\w{0,6}.{1,5}\bобл",
        "Cherkasy": r"(?i)\bЧЕРКАC\w{0,6}.{1,5}\bобл",
        "Kropyvnytskyi": r"(?i)\bК[іи]РОВОГРАДС\w{0,6}.{1,5}\bобл",
        "Odesa": r"(?i)\bОДЕС\w{0,6}.{1,5}\bобл",
        "Mykolaiv": r"(?i)\b[мн]ИКОЛА[їеє]ВС\w{0,6}.{1,5}\bобл",
        "Kherson": r"(?i)\bХЕРСОНС\w{0,6}.{1,5}\bобл",
        "Simferopol": r"(?i)\bКР\w{1,2}М\b|\bСЕВАСТ\w{0,1}ПОЛ\w{1,10}\b|\bЯЛТ\w{1,10}|\bАР\b|\bС[іи]МФЕРОПОЛ\w{1,10}\b",
        "Zaporizhzhia": r"(?i)\bЗАПОР[іо]\w{0,6}.{1,5}\bобл",
        "Dnipro": r"(?i)\bДН[іе]ПРОПЕТРОВС\w{0,6}.{1,5}\bобл",
        "Poltava": r"(?i)\bПОЛТАВС\w{0,6}.{1,5}\bобл",
        "Chernihiv": r"(?i)\bЧЕРН[іи]Г[іо]В\w{0,6}.{1,5}\bобл",
        "Sumy": r"(?i)\bСУМ\w{0,6}.{1,5}\bобл",
        "Kharkiv": r"(?i)\bХАР\w{0,1}К[іо]В\w{0,6}.{1,5}\bобл",
        "Luhansk": r"(?i)\bЛУГАНС\w{0,6}.{1,5}\bобл",
        "Donetsk": r"(?i)\bДОНЕЦ\w{0,6}.{1,5}\bобл",
    }
    # Dictionary with administrative centers' names (keys) and their respective regular expressions (values)
    regex_acenters = {
        "Uzhhorod": r"(?i)\bУЖГОРОД\w{0,6}\b",
        "Lviv": r"(?i)\bЛЬВ[іо]В\w{0,6}\b",
        "Ivano-Frankivsk": r"(?i)\b[іи]В\w{0,3}[.\-]ФРАНК\w{0,3}ВС\w{0,6}\b",
        "Chernivtsi": r"(?i)\bЧЕРН[іо]В\w{0,1}Ц\w{0,6}\b",
        "Ternopil": r"(?i)\bТЕРНОП[іо]ЛЬ\w{0,6}\b",
        "Lutsk": r"(?i)\bВОЛ\w{1,2}Н\w{0,6}\b|\bЛУЦ\w{0,1}К\w{0,6}\b",
        "Rivne": r"(?i)\bР[іо]ВН[ео]\w{0,6}\b|\bГОЩАНС\w{0,5}\b",
        "Zhytomyr": r"(?i)\bЖИТОМИР\w{0,6}\b",
        "Khmelnytskyi": r"(?i)\bХМЕЛЬНИЦ\w{0,6}\b",
        "Vinnytsia": r"(?i)\bВ[іи]ННИЦ\w{0,6}\b",
        "Kyiv": r"(?i)\bКИ[їеє]В\w{0,6}\b|\bПЕЧЕРСЬК\w{0,6}\b|\bГОЛОСІЇВ\w{0,6}\b",
        "Cherkasy": r"(?i)\bЧЕРКАС\w{0,6}\b",
        "Kropyvnytskyi": r"(?i)\bК[іи]РОВОГРАД\w{0,6}\b|\bКРОПИВНИЦ\w{0,6}\b",
        "Odesa": r"(?i)\bОДЕС\w{0,6}\b",
        "Mykolaiv": r"(?i)\b[мн]ИКОЛА[їеє]В\w{0,6}\b",
        "Kherson": r"(?i)\bХЕРСОН\w{0,6}\b",
        "Simferopol": r"(?i)\bКР\w{1,2}М\b|\bСЕВАСТ\w{0,1}ПОЛ\w{1,10}\b|\bЯЛТ\w{1,10}|\bАР\b|\bС[іи]МФЕРОПОЛ\w{1,10}\b",
        "Zaporizhzhia": r"(?i)\bЗАПОР[іо]\w{0,6}\b",
        "Dnipro": r"(?i)\bДН[іе]ПР\w{0,10}\b|\bДН[іе]ПРОПЕТРОВС\w{0,6}\b|\bКРИВ\w{0,3}\W{0,5}Р\w{1,6}\b",
        "Poltava": r"(?i)\bПОЛТАВ\w{0,6}\b",
        "Chernihiv": r"(?i)\bЧЕРН[іи]Г[іо]В\w{0,6}\b|\bН[іе]ЖИН\w{0,6}\b|\bБАХМА\w{0,6}\b",
        "Sumy": r"(?i)\bСУМ\w{0,6}\b|\bЛЮБОТ\w{1,6}\b",
        "Kharkiv": r"(?i)\bХАР\w{0,1}К[іо]В\w{0,6}\b|\bЛОЗОВ\w{0,6}\b|\bОСНОВ\w{0,6}\b",
        "Luhansk": r"(?i)\bЛУГАНС\w{0,6}\b",
        "Donetsk": r"(?i)\bДОНЕЦ\w{0,6}\b",
    }

    try:
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
        df = df.with_columns(region_col.alias("region")).drop("organunit")

        # Materialize and compute data info only if logger level is DEBUG
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Rows: {df.select(pl.len()).collect().item():,}")
            logger.debug(f"Schema: {df.collect_schema()}")
            logger.debug(f"Sample: {df.head(1).collect()}")

        return df

    except Exception as e:
        logger.error(f"Region mapping failed: {e}")
        sys.exit(1)


def transform_column_weaponcategory(df: pl.LazyFrame) -> tuple[pl.LazyFrame, pl.LazyFrame]:
    """Creates a new column with broader weapon categories. Creates column 'weaponcategory'.

    Args:
        df (pl.LazyFrame): Post-exctraction data.

    Returns:
        tuple[pl.LazyFrame, pl.LazyFrame]: Lazy query plans for data with original weapon names and additional weapon mappings .
    """
    
    # Temporary Series objects below will be later used to populate temporary DataFrame
    bladed = pl.LazyFrame(
        data={"Bladed":[
            "КИНДЖАЛ",
            "КОРТИК",
            "МЕЧ",
            "НІЖ МИСЛИВСЬКИЙ",
            "НІЖ",
            "ШАБЛЯ",
            "ШАШКА",
            "ШТИК НІЖ",
            "ШТИК",
        ]},
        schema={"Bladed":pl.String}
    )
    handguns = pl.LazyFrame(
        data={"Handguns":[
            "ПІСТОЛЕТ ГАЗОВИЙ",
            "ПІСТОЛЕТ КУЛЕМЕТ",
            "ПІСТОЛЕТ МК",
            "ПІСТОЛЕТ ПІД ГУМОВУ КУЛЮ",
            "ПІСТОЛЕТ САМОРОБНИЙ",
            "ПІСТОЛЕТ СИГНАЛЬНИЙ",
            "ПІСТОЛЕТ СТАРТОВИЙ",
            "ПІСТОЛЕТ",
            "РЕВОЛЬВЕР ГАЗОВИЙ",
            "РЕВОЛЬВЕР ГАЗОВОДРОБОВИЙ",
            "РЕВОЛЬВЕР ПІД ГУМОВУ КУЛЮ",
            "РЕВОЛЬВЕР СИГНАЛЬНИЙ",
            "РЕВОЛЬВЕР СТАРТОВИЙ",
            "РЕВОЛЬВЕР",
            "ПІСТОЛЕТ АВТОРУЧКА",
        ]},
        schema={"Handguns":pl.String}
    )
    lfirearms = pl.LazyFrame(
        data={"Light firearms":[
            "АВТОМАТ",
            "ГВИНТІВКА МК",
            "ГВИНТІВКА",
            "КАРАБІН",
            "ОБРІЗ ГВИНТІВКИ МК",
            "ОБРІЗ ГВИНТІВКИ",
            "ОБРІЗ КАРАБІНА",
            "ОБРІЗ РУШНИЦІ",
            "РУШНИЦЯ ЗБІРНА",
            "РУШНИЦЯ МИСЛИВСЬКА",
            "РУШНИЦЯ ПОМПОВА",
            "РУШНИЦЯ",
        ]},
        schema={"Light firearms":pl.String}
    )
    hfirearms = pl.LazyFrame(
        data={"Heavy firearms":[
            "ГАРМАТА АВТОМАТИЧНА",
            "ГАРМАТА",
            "КУЛЕМЕТ СТАНКОВИЙ",
            "КУЛЕМЕТ",
            "РУШНИЦЯ ПРОТИТАНКОВА",
        ]},
        schema={"Heavy firearms":pl.String}
    )
    pneaumaticflob = pl.LazyFrame(
        data={"Pneumatic&Flobert":[
            "ГВИНТІВКА ПНЕВМАТИЧНА",
            "КАРАБІН ПІД ПАТРОН ФЛОБЕРА",
            "ПІСТОЛЕТ ПІД ПАТРОН ФЛОБЕРА",
            "ПІСТОЛЕТ ПНЕВМАТИЧНИЙ",
            "РЕВОЛЬВЕР ПІД ПАТРОН ФЛОБЕРА",
            "РЕВОЛЬВЕР ПНЕВМАТИЧНИЙ",
        ]},
        schema={"Pneumatic&Flobert":pl.String}
    )
    artillery = pl.LazyFrame(
        data={"Artillery":[
            "ГРАНАТОМЕТ",
            "МІНОМЕТ",
            "ПЗРК",
            "ПТРК",
            "РАКЕТНИЦЯ",
            "ПУСКОВІ УСТАНОВКИ",
            "ЗЕНІТНА УСТАНОВКА",
        ]},
        schema={"Artillery":pl.String}
    )
    explosives = pl.LazyFrame(
        data={"Explosives":[
            "ВИБУХОВІ РЕЧОВИНИ",
            "ГРАНАТА",
            "РАКЕТА",
            "СНАРЯД"
        ]},
        schema={"Explosives":pl.String}
    )
    other = pl.LazyFrame(
        data={"Other":[
            "ДЕТАЛІ",
            "ЗАПАЛ",
            "ЗАТВОР ДЕТАЛЬ",
            "ІНШІ ДЕТАЛІ ЗБРОЇ",
            "МАГАЗИН ПІСТОЛЕТНИЙ",
            "МАГАЗИН",
            "НАБОЇ БОЄВІ",
            "ПРИЦІЛ ОПТИЧНИЙ",
            "РАМКА ДЕТАЛЬ",
            "СТВОЛ ДЕТАЛЬ",
            "СТВОЛЬНА КОРОБКА ДЕТАЛЬ",
            "АРБАЛЕТ",
            "РУШНИЦЯ ДЛЯ ПІДВОДНОГО ПОЛЮВАННЯ",
            "АВТОМАТ УЧБОВИЙ",
            "ГВИНТІВКА УЧБОВА",
            "КАРАБІН УЧБОВИЙ",
            "КУЛЕМЕТ УЧБОВИЙ",
            "ПІСТОЛЕТ МОНТАЖНИЙ",
            "ПІСТОЛЕТ УЧБОВИЙ",
            "КИСТЕНЬ",
        ]},
        schema={"Other":pl.String}
    )

    try:
        # Concatenate LazyFrames into a single one
        wps_df = pl.concat(
            [bladed, handguns, lfirearms, hfirearms, pneaumaticflob, artillery, explosives, other],
            how="horizontal"
        )
    except pl.ShapeError as e:
        logger.error(f"Concatenation failed. Shape mismatch: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to concatenate LazyFrames: {e}")
        sys.exit(1)

    try:
        # Unpivot LazyFrame (columns to rows)
        wps_df = wps_df.unpivot(variable_name="weaponcategory", value_name="weaponkind").drop_nulls()
    except pl.ColumnNotFoundError as e:
        logger.error(f"Unpivot failed. Key column missing: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to unpivot LazyFrame: {e}")
        sys.exit(1)

    try:
        # Join weapon names with matching weapon categories 
        df = df.join(other=wps_df, on="weaponkind", how="left")
    except pl.ColumnNotFoundError as e:
        logger.error(f"Join failed. Key column missing: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to join weapon names with matching weapon categories: {e}")
        sys.exit(1)

    # Materialize and compute data info only if logger level is DEBUG
    if logger.isEnabledFor(logging.DEBUG):
        _nulls = (
            df
            .null_count()
            .unpivot(
                variable_name='column',
                value_name='total_nulls'
                )
            .select(['column', 'total_nulls'])
            .collect()
            .rows()
            
        )
        logger.debug(f"Rows: {df.select(pl.len()).collect().item():,}")
        logger.debug(f"Nulls: {_nulls}")
        logger.debug(f"Sample: {df.head(1).collect()}")

    return df, wps_df 


def check_new_weapons(df: pl.LazyFrame, wps_df: pl.LazyFrame) -> pl.LazyFrame:
    """Checks for new weapons, drops nulls redundant 'weaponkind' column, and removes rows with missing weapon categories.

    Args:
        df (pl.LazyFrame): Lazy query plan for data with original weapon names.
        wps_df (pl.LazyFrame): Lazy query plan for additional weapon mappings.

    Returns:
        pl.LazyFrame: Query plan (LazyFrame).
    """

    # Check wether any new weapons are present in a dataset
    has_null = df.select(pl.col("weaponcategory").is_null().any()).collect().item()
    if has_null:

        new_weapons = set()
        count = 0

        wep_list = (
            df
            .filter(pl.col("weaponcategory").is_null())
            .select("weaponkind")
            .collect()
            .get_column("weaponkind")
            .to_list()
        )

        for w in wep_list: 
            if w not in wps_df.collect().get_column("weaponkind"):
                new_weapons.add(w)
                count += 1

        logger.warning(f"{count} records of {len(new_weapons)} new weapons present: {str(new_weapons)[1:-1]}.\
                    \nUpdate 'wps_df' with new weapons!")
    else:
        logger.info("No records with new weapons found.")

    df = df.drop("weaponkind").drop_nulls()

    # Materialize and compute data info only if logger level is DEBUG
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Rows: {df.select(pl.len()).collect().item():,}")
        logger.debug(f"Schema: {df.collect_schema()}")
        logger.debug(f"Sample: {df.head(1).collect()}")

    return df
    

def transform_column_date(df: pl.LazyFrame) -> pl.LazyFrame:
    """Creates a new date column using/replacing 'theftdate' and 'insertdate'.
    Removes and substitutes records preserving historical accuracy during post-independence period.

    Args:
        df (pl.LazyFrame): Post-extraction data.

    Returns:
        pl.LazyFrame: Query plan (LazyFrame).
    """

    # Substituting missing values in theftdate with those from the insertdate column
    df = df.with_columns(pl.coalesce(["theftdate","insertdate"]).alias("date"))

    # Dropping redundant date columns
    df = df.drop("insertdate","theftdate")

    # Excluding Ukrainian SSR records from DataFrame
    try:
        _dt_independence = datetime(year=1991, month=8, day=24)
        df = df.filter(pl.col("date") >= _dt_independence).sort(by="date", descending=False)
        logger.debug(f"Rows: {df.select(pl.len()).collect().item():,}")
        logger.debug(f"Schema: {df.collect_schema()}")

    except Exception as e:
        logger.error(f"Failed while excluding pre-independence records: {e}")
        sys.exit(1)

    # Crimean records
    try:
        date_col = pl.col("date")

        _last_dt_crimea = datetime(year=2014, month=3, day=24)
        crimea_cond = (pl.col("region") == "Simferopol")&(pl.col("date") > _last_dt_crimea)

        date_col = pl.when(crimea_cond).then(pl.lit(_last_dt_crimea)).otherwise(date_col).alias("date")

        df = df.with_columns(date_col)

    except Exception as e:
        logger.error(f"Failed while substituting post-2014 Crimea dates: {e}")
        sys.exit(1)


    # Materialize and compute data info only if logger level is DEBUG
    if logger.isEnabledFor(logging.DEBUG):
        _nulls = (
            df
            .null_count()
            .unpivot(variable_name='column', value_name='total_nulls')
            .select(['column', 'total_nulls'])
            .collect()
            .rows()
        )
        logger.debug(f"Rows: {df.select(pl.len()).collect().item():,}")
        logger.debug(f"Schema: {df.collect_schema()}")
        logger.debug(f"Sample (First ever record): {df.head(1).collect()}")
        logger.debug(f"Sample (Max date for Crimea): {df.filter(pl.col('region')=='Simferopol').tail(1).collect()}")
        logger.debug(f"Nulls: {_nulls}")

    return df

###############################################################
                    # SCRIPT SPLIT HERE
###############################################################

def sort_columns (df: pl.LazyFrame) -> pl.LazyFrame:

    df = df.match_to_schema({
        "report": pl.String,
        "region": pl.String, 
        "weaponcategory": pl.String, 
        "date": pl.Datetime("us")
    })
    df = df.sort(by=["date", "region"], descending=False)
    
    return df


def export_data(df: pl.LazyFrame, output_path: str) -> None:
    """Exports data to gzip compressed parquet file.

    Args:
        df (pl.LazyFrame): Sorted and reordered LazyFrame.
        output_path: File path to which the data should be wrtitten.
    """

    df.sink_parquet(
        path=output_path,
        compression="gzip"
    )
    logger.info(f"Exported data to {None}.")
    return None

if __name__ == "__main__":
    # (
    #     import_data()
    #     .pipe(cast_dtypes)
    #     .pipe(transform_column_reasonsearch)
    #     .pipe(transform_column_region)
    #     .pipe(transform_column_weaponcategory)
    #     .pipe(transform_column_date)
    #     .pipe(export_data)
    # )
    # print(f"\n✅ Data Successfuly Exported To: assets/ua-mia-weapons.parquet.gzip\n")
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
        
        logger.info("2/4 Transform 'region' column...")
        df = transform_column_region(df)

        logger.info("3/4 Transform 'weaponcategory' column...")
        df, wps_df = transform_column_weaponcategory(df)
        df = check_new_weapons(df, wps_df)

        logger.info("4/4 Transform 'date' column...")
        df = transform_column_date(df)

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

    print(pd.read_parquet("ua-mia-weapons.parquet.gzip").head())

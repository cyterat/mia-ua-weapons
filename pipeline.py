import os
import sys
import logging
from datetime import datetime

import polars as pl
import polars.selectors as cs


# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEBUG_MODE = logger.isEnabledFor(logging.DEBUG)
INPUT_PATH = os.path.join("assets","weapons-wanted.json")
OUTPUT_PATH = os.path.join("assets","ua-mia-weapons.parquet.gzip")


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


def transform_column_region(df: pl.LazyFrame) -> pl.LazyFrame:
    """Replaces long MIA unit names with region names using regex. Creates column 'region'.

    Args:
        df (pl.LazyFrame): Post-extraction query plan (LazyFrame).

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

    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE)

    return df


def transform_column_weaponcategory(df: pl.LazyFrame) -> tuple[pl.LazyFrame, pl.LazyFrame]:
    """Creates a new column with broader weapon categories. Creates column 'weaponcategory'.

    Args:
        df (pl.LazyFrame): Post-extraction query plan (LazyFrame).

    Returns:
        tuple[pl.LazyFrame, pl.LazyFrame]: Lazy query plans for data with original weapon names and additional weapon mappings.
    """
    
    # Temporary Series objects below will be later used to populate a DataFrame
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

    # Concatenate LazyFrames into a single one
    wps_df = pl.concat(
        [bladed, handguns, lfirearms, hfirearms, pneaumaticflob, artillery, explosives, other],
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

        logger.warning(f"{count} records of {len(new_weapons)} new weapons present: {str(new_weapons)[1:-1]}.\
                    \nUpdate 'wps_df' with new weapons!")
    else:
        logger.info("No records with new weapons found.")

    # Drop redundant column
    df = df.drop("weaponkind")
    # Drop all rows that contain any nulls
    df = df.drop_nulls()

    # Generate info logs if logger level is DEBUG
    enable_debug_logs(df, is_debug=DEBUG_MODE)

    return df
    

def transform_column_date(df: pl.LazyFrame) -> pl.LazyFrame:
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
        compression="gzip"
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
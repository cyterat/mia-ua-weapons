import pandas as pd
import numpy as np

import os


def import_data():
    print("\n1/7 Import data...")
    
    def get_lfs_json_path():
        """
        Returns JSON data file path using LFS OID.
        Throws an AssertionError if file is not found.
        """
        # Path to the oid.txt artifact 
        oid_file_path = "assets/oid.txt"
        
        # Check if OID artifact path exists.
        assert os.path.exists(oid_file_path), "oid.txt artifact path does not exist."
        
        # Read oid.txt contents into file
        with open(oid_file_path, "r") as file:
            oid = file.read() 
        
        # The path to JSON file given OID
        lfs_json_dir = f".git/lfs/objects/{oid[0:2]}/{oid[2:4]}/{oid}"

        print("OID:", oid)
        return lfs_json_dir

    # Read the JSON data file into a Pandas DataFrame
    parsed = pd.read_json(get_lfs_json_path(), orient="records")

    print("☑️ Data imported:")
    print(f"\nRows --> {parsed.shape[0]:,}")
    print(f"Columns --> {parsed.shape[1]}")
    print(f"Memory usage --> {int(parsed.memory_usage(deep=True).sum()/1000000)} MB")
    print(f"\nMissing values:\n{parsed.isna().sum() + parsed[parsed == ''].count()}")
    return parsed


def cast_dtypes(parsed):
    print("\n2/7 Cast data types...")

    df = parsed.loc[
        :,
        [
            "weaponnumber",
            "weaponkind",
            "organunit",
            "reasonsearch",
            "insertdate",
            "theftdate",
        ],
    ].copy()

    # Removing duplicates
    df = df.drop_duplicates()

    # Cast date and other columns to 'datetime64[ns]' and 'string' types respectively
    for c in df.columns:
        if c in ["insertdate", "theftdate"]:
            df[c] = pd.to_datetime(df[c], errors="coerce")
        else:
            df[c] = df[c].astype("string")

    print(f"\nRows --> {df.shape[0]:,}")
    print(f"Columns --> {df.shape[1]}")
    print("☑️ Data types casted")
    return df


def column_reasonsearch(df):
    print("\n3/7 Clean 'reasonsearch' column...")

    # Removing records with missing "reasonsearch" value
    df = df.drop(index=df[df["reasonsearch"] == ""].index)

    df["reasonsearch"] = df["reasonsearch"].str.title()

    # Renaming (translating) values
    df["reasonsearch"] = df["reasonsearch"].replace("Викрадення", "Theft")
    df["reasonsearch"] = df["reasonsearch"].replace("Втрата", "Loss")

    df = df.rename(columns={"reasonsearch": "report"})
    df["report"] = df["report"].astype("string")

    print(f"\nRows --> {df.shape[0]:,}")
    print(f"Columns --> {df.shape[1]}")
    print("☑️ Column 'reasonsearch' cleaned")
    return df


def column_region(df):
    print("\n4/7 Create 'region' column...")

    # Removing records with missing "organunit" value
    df = df.drop(index=df[df["organunit"] == ""].index)

    tmp_region = df["organunit"].astype(str)
    # Creating dictionary with oblasts names (keys) and their respective regular expressions (values)
    regx_oblasts = {
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
    # Creating dictionary with administrative centers' names (keys) and their respective regular expressions (values)
    regx_acenters = {
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

    # 1st Searching for oblasts in "tmp_region" and replacing them with their respective region names from "regx_oblasts"
    for k, v in regx_oblasts.items():
        tmp_region[tmp_region.str.contains(regx_oblasts[k])] = str(k)

    # 2nd Searching for cities, districts, towns, etc., in "tmp_region" and replacing them with their respective region names from "regx_acenters"
    for k, v in regx_acenters.items():
        tmp_region[tmp_region.str.contains(regx_acenters[k])] = str(k)

    tmp_region = tmp_region.rename("region")

    # Joining "region" column to the original dataframe
    df = df.join(tmp_region, how="left")  # joins on index by default
    df.head(1)

    # Removing ambiguous records from the DataFrame
    df = df[df["region"].isin(regx_acenters.keys())]

    # Removing "organunit" column
    df = df.drop(columns=["organunit"])

    # Casting values to string data type
    df["region"] = df["region"].astype("string")

    print(f"\nRows --> {df.shape[0]:,}")
    print(f"Columns --> {df.shape[1]}")
    print("☑️ 'region' column created")
    return df


def column_weaponcategory(df):
    print("\n5/7 Create 'weaponcategory' column...")

    # Removing records with missing "weaponkind" value
    df = df.drop(index=df[df["weaponkind"] == ""].index)

    # Temporary Series objects below will be later used to populate temporary DataFrame
    bladed = pd.Series(
        [
            "КИНДЖАЛ",
            "КОРТИК",
            "МЕЧ",
            "НІЖ МИСЛИВСЬКИЙ",
            "НІЖ",
            "ШАБЛЯ",
            "ШАШКА",
            "ШТИК НІЖ",
            "ШТИК",
        ]
    )
    handguns = pd.Series(
        [
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
        ]
    )
    lfirearms = pd.Series(
        [
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
        ]
    )
    hfirearms = pd.Series(
        [
            "ГАРМАТА АВТОМАТИЧНА",
            "ГАРМАТА",
            "КУЛЕМЕТ СТАНКОВИЙ",
            "КУЛЕМЕТ",
            "РУШНИЦЯ ПРОТИТАНКОВА",
        ]
    )
    pneaumaticflob = pd.Series(
        [
            "ГВИНТІВКА ПНЕВМАТИЧНА",
            "КАРАБІН ПІД ПАТРОН ФЛОБЕРА",
            "ПІСТОЛЕТ ПІД ПАТРОН ФЛОБЕРА",
            "ПІСТОЛЕТ ПНЕВМАТИЧНИЙ",
            "РЕВОЛЬВЕР ПІД ПАТРОН ФЛОБЕРА",
            "РЕВОЛЬВЕР ПНЕВМАТИЧНИЙ",
        ]
    )
    artillery = pd.Series(
        [
            "ГРАНАТОМЕТ",
            "МІНОМЕТ",
            "ПЗРК",
            "ПТРК",
            "РАКЕТНИЦЯ",
            "ПУСКОВІ УСТАНОВКИ",
            "ЗЕНІТНА УСТАНОВКА",
        ]
    )
    explosives = pd.Series(["ВИБУХОВІ РЕЧОВИНИ", "ГРАНАТА", "РАКЕТА", "СНАРЯД"])
    other = pd.Series(
        [
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
        ]
    )

    wps_df = pd.DataFrame(
        {
            "Bladed": bladed,
            "Handguns": handguns,
            "Light firearms": lfirearms,
            "Heavy firearms": hfirearms,
            "Pneumatic&Flobert": pneaumaticflob,
            "Artillery": artillery,
            "Explosives": explosives,
            "Other": other,
        }
    )

    # Unpivoted DataFrame
    melted_df = wps_df.melt(var_name="weaponcategory", value_name="weaponkind").dropna()

    # Adding a newly created column to the main dataframe
    df = df.merge(right=melted_df, how="left", on="weaponkind")

    # Casting values to string data type
    df["weaponcategory"] = df["weaponcategory"].astype("string")

    # Check wether any new weapons are present in a dataset
    if df["weaponcategory"].count() != df["region"].count():
        new_weapons = set()
        count = 0

        # Check current DataFrame weapons against previous ones (stored in Series objects)
        for r in df["weaponkind"].values:
            if (
                r
                not in pd.concat(
                    [
                        bladed,
                        handguns,
                        lfirearms,
                        hfirearms,
                        pneaumaticflob,
                        artillery,
                        explosives,
                        other,
                    ],
                    axis=0,
                ).values
            ):
                new_weapons.add(r)
                count += 1

        print(f"\n Number of unique entries --> {str(df['weaponkind'].nunique())}")
        print(
            f"\n❗️ {count} records of {len(new_weapons)} new weapons present: {str(new_weapons)[1:-1]}"
        )
        print("Update 'wps_df' Series objects with new weapons!")

    print(f"\nRows --> {df.shape[0]:,}")
    print(f"Columns --> {df.shape[1]}")
    print("☑️ Column 'weaponcategory' created")
    return df


def column_date(df):
    print("\n6/7 Create 'date' column...")

    # Substituting missing values with those from the adjacent column
    df["theftdate"] = df["theftdate"].combine_first(df["insertdate"])

    # Dropping "insertdate" column since it is no longer needed
    df = df.drop("insertdate", axis=1)

    # Removing records with missing "theftdate" value
    df = df.drop(index=df[df["theftdate"] == ""].index)

    # Renaming column to "date"
    df = df.rename(columns={"theftdate": "date"})

    # Excluding Ukrainian SSR records from DataFrame
    df = df[df["date"] >= "1991-08-24"].sort_values(by="date").reset_index(drop=True)

    # Crimean records
    # Storing 'argwhere' arrays in a variable
    cond_args = np.argwhere(
        [(df.loc[:, "region"] == "Simferopol") & (df.loc[:, "date"] >= "2014-03-25")]
    )

    # Overwriting main dataframe values with '2014-03-24', using 'cond_args' indexes
    for _, index in cond_args:
        df.loc[index, "date"] = pd.to_datetime("2014-03-24").tz_localize(None)

    print(f"\nRows --> {df.shape[0]:,}")
    print(f"Columns --> {df.shape[1]}")
    print("☑️ 'date' column created")
    return df


def export_data(df):
    print("\n7/7 Export data...")

    assert df.shape[0] != 0, "\n❗️ Dataframe is empty"

    # Rearranging and sorting columns
    end_df = (
        df.loc[:, ["date", "region", "report", "weaponcategory"]]
        .sort_values(by=["date", "region"])
        .reset_index(drop=True)
        .copy()
    )

    print("\n...")
    print(end_df.head(1))
    print("...\n")

    print(f"Rows --> {end_df.shape[0]:,}")
    print(f"Columns --> {end_df.shape[1]}")
    print(f"Memory usage --> {int(end_df.memory_usage(deep=True).sum()/1000000)} MB")
    print(f"\nMissing values:\n{end_df.isna().sum() + end_df[end_df == ''].count()}")

    end_df.to_parquet(
        "assets/ua-mia-weapons.parquet.gzip",
        engine="pyarrow",
        compression="gzip",
        index=False,
    )


if __name__ == "__main__":
    (
        import_data()
        .pipe(cast_dtypes)
        .pipe(column_reasonsearch)
        .pipe(column_region)
        .pipe(column_weaponcategory)
        .pipe(column_date)
        .pipe(export_data)
    )
    print(f"\n✅ Data Successfuly Exported To: assets/ua-mia-weapons.parquet.gzip\n")

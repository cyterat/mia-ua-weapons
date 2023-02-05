import pandas as pd
import numpy as np

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Boilerplate aggregation-functions
from common.eda import aggregator, country_stats


def import_data():
    try:
        # File object
        file = "assets/ua-mia-weapons.parquet.gzip"

        # Reading the parquet output into a DataFrame
        df = pd.read_parquet(file)
        
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")
    
    return df


def agg_weapon_ctgr():
    print('\n* Create "agg-weapon-ctgr.parquet.gzip" file...')

    try:
        tmp_df = (
            aggregator(df, frequency='Y')
            .groupby(['weaponcategory'])['frequency']
            .sum()
            .reset_index(name='total')
            .set_index('weaponcategory')
            )

        tmp_df = tmp_df.sort_values(by='total', ascending=False).rename_axis(index=None)
        tmp_df = tmp_df.assign(percentage=tmp_df.div(tmp_df.sum(axis=0), axis=1))
    
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")

    
    print('File created')
    tmp_df.to_parquet('assets/models/agg-weapon-ctgr.parquet.gzip', engine='pyarrow', compression='gzip', index=True)


def c_stats():
    print('\n* Create "country-stats.parquet.gzip" file...')

    try:
        tmp_df = country_stats(aggregator(df, pivot=True))

    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")
    

    print('File created')
    tmp_df.to_parquet('assets/models/country-stats.parquet.gzip', engine='pyarrow', compression='gzip', index=False)


def region_tl():
    print('\n* Create "regions-tl" file...')

    try:
        tmp_df = (
            aggregator(df, pivot=True)
            .groupby(['region','date'])['frequency', 'loss','theft']
            .sum()
            .reset_index()
            .rename(columns={'frequency':'total'})
            )

    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")


    print('File created')
    tmp_df.to_parquet('assets/models/regions-tl.parquet.gzip', engine='pyarrow', compression='gzip', index=False)
   

def cat_ua_df():
    print('\n* Create "cat-ua-df" file...')

    try:
        tmp_df = aggregator(df, frequency='Y')

        tmp_df = (
            tmp_df
            .groupby(['region','weaponcategory'])
            .agg({'frequency':['sum']})
            .fillna(0)
            .xs("sum", level=1, axis=1, drop_level=True)
            .reset_index()
        )
    
        # Exclude weapon categories with no records in their respective region
        tmp_df = tmp_df[tmp_df['frequency']!=0]

        # Weapon categories ranks in their region (Rank 1 == weapon with the largest number of records in a region)
        tmp_df['local_rank'] = (
            tmp_df
            .groupby(['region'])['frequency']
            .rank(method='dense', ascending=False)
            .astype('int8')
        )

        # Regional weapon categories ranks among all other regions in the country 
        # (Rank 1 == weapon category of a specific region has the largest number of records in the country)
        tmp_df['country_rank'] = (
            tmp_df['frequency']
            .rank(method='dense', ascending=False)
            .astype('int32')
        )

        # Log (base 100) of each weapon category in every region (used for marker sizes in the visualisation)
        tmp_df['freqLog100'] = np.log(tmp_df['frequency']) / np.log(100) #log base 100

        # Total number of cases in a region
        tmp_df = (
            tmp_df
            .join(
                tmp_df.groupby(['region']).agg({'frequency':'sum'}), 
                on='region',
                how='inner',
                rsuffix='r'
            )
            .rename(
                columns={'frequencyr':'total_region'}
                )
        )

        # Total number of cases in the country
        tmp_df['total_country'] = tmp_df['frequency'].sum().astype('int64') #'freqCountry'
        
        # Sorting values by region and weapon category
        tmp_df = tmp_df.sort_values(['region', 'weaponcategory']).reset_index(drop=True)

    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")


    print('File created')
    tmp_df.to_parquet('assets/models/cat-ua-df.parquet.gzip', engine='pyarrow', compression='gzip', index=False)


def histogram():
    print('\n* Create "histogram" file...')

    try:
        tmp_df = (
            aggregator(df, 'M')
            .groupby(['date'])
            .sum(numeric_only=True)
            .reset_index()
            )

    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")


    print('File created')
    tmp_df.to_parquet('assets/models/histogram.parquet.gzip', engine='pyarrow', compression='gzip', index=True)


def yr_weekly_scats():
    print('\n* Create "yr-weekly-scats" file...')

    try:
        tmp_df = (
            aggregator(df, 'W')
            .groupby(['date', 'report'])
            .sum(numeric_only=True)
            .reset_index()
            )
    
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")


    print('File created')
    tmp_df.to_parquet('assets/models/yr-weekly-scats.parquet.gzip', engine='pyarrow', compression='gzip', index=True)


def top5():
    print('\n* Create "top5" file...')

    try:
        tmp_df = country_stats(aggregator(df, pivot=True)).set_index('region').nlargest(5,'frequency')
        tmp_df = tmp_df.iloc[tmp_df['frequency'].argsort()[::-1],:].reset_index()
        tmp_df = tmp_df.set_index('region').iloc[:,:2]
        tmp_df = tmp_df.iloc[::-1,::-1]
    
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")

    print('File created')
    tmp_df.to_parquet('assets/models/top5.parquet.gzip', engine='pyarrow', compression='gzip', index=True)


def tls_ratio():
    print('\n* Create "tls-ratio" file...')

    try:
        tmp_df = (
            aggregator(df)
            .groupby(["report"])
            .agg('sum', numeric_only=True)
            .reset_index()
            )
    
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")

    print('File created\n')
    tmp_df.to_parquet('assets/models/tls-ratio.parquet.gzip', engine='pyarrow', compression='gzip', index=True)




if __name__=='__main__':

    df = import_data()

    assert set(df.columns) == set(['date','region','report','weaponcategory']), "DataFrame should have the following columns: 'date', 'region', 'report', 'weaponcategory'"

    agg_weapon_ctgr()
    c_stats()
    region_tl()
    cat_ua_df()
    histogram()
    yr_weekly_scats()
    top5()
    tls_ratio()

    print('Finished running the script\n')
    

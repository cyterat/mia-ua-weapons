import pandas as pd
import numpy as np


def import_data():
    print('\n* Import "ua-mia-weapons.parquet.gzip" file...')

    file = "assets/ua-mia-weapons.parquet.gzip"

    df = pd.read_parquet(file)
    
    return df


def model_month_total():
    print('\n* Create "month-total" file...')

    tmp_df = (
        df
        .groupby(pd.Grouper(key='date',freq='M'))['report']
        .count()
        .reset_index()
        .rename(columns={"report": "total"})
        .astype({
            "date":"datetime64[ns]",
            "total":"int32"
            })
        )

    print('File created')
    tmp_df.to_parquet('assets/models/month-total.parquet.gzip', engine='pyarrow', compression='gzip', index=False)


def model_date_report_total():
    print('\n* Create "date-report-total" file...')

    tmp_df = (
        df
        .groupby([pd.Grouper(key='date',freq='D'),'report'])['region']
        .count()
        .reset_index()
        .rename(columns={"region": "total"})
        .astype({
            "total":"int32",
            "date":"datetime64[ns]",
            "report":"string"
            })
        )

    tmp_df.to_parquet('assets/models/date-report-total.parquet.gzip', engine='pyarrow', compression='gzip', index=False)
    print('File created')


def model_weaponcategory_total():
    print('\n* Create "weaponcategory-total.parquet.gzip" file...')

    tmp_df = (
        df
        .groupby(['weaponcategory'])['report']
        .count()
        .reset_index()
        .rename(columns={'report':'total'})
        .assign(
            loss = (
                df[df['report']=='Loss']
                .groupby(['weaponcategory'])['report']
                .count()
                .values
                )
            )
        .assign(
            theft = (
                df[df['report']=='Theft']
                .groupby(['weaponcategory'])['report']
                .count()
                .values
                )
            )
        .astype({
            'weaponcategory':'string',
            'total':'int32',
            'loss':'int32',
            'theft':'int32'
            })
        .sort_values(
            'total',
            ascending=False,
            ignore_index=True
            )
        )
    
    print('File created')
    tmp_df.to_parquet('assets/models/weaponcategory-total.parquet.gzip', engine='pyarrow', compression='gzip', index=False)


def model_region_total():
    print('\n* Create "region-total.parquet.gzip" file...')

    tmp_df = (
        df
        .groupby(['region'])['report']
        .count()
        .reset_index()
        .rename(columns={'report':'total'})
        .assign(
            loss = (
                df[df['report']=='Loss']
                .groupby(['region'])['report']
                .count()
                .values
                )
            )
        .assign(
            theft = (
                df[df['report']=='Theft']
                .groupby(['region'])['report']
                .count()
                .values
                )
            )
        .astype({
            'region':'string',
            'total':'int32',
            'loss':'int32',
            'theft':'int32'
            })
        .sort_values(
            'total',
            ascending=False,
            ignore_index=True
            )
        )
    
    tmp_df = (
        tmp_df
        .assign(total_pct=tmp_df['total'] / tmp_df['total'].sum())
        .assign(loss_pct=tmp_df['loss'] / tmp_df['total'])
        .assign(theft_pct=tmp_df['theft'] / tmp_df['total'])
        .astype({
            'total_pct':'float32',
            'loss_pct':'float32',
            'theft_pct':'float32',
            })
        )

    print('File created')
    tmp_df.to_parquet('assets/models/region-total.parquet.gzip', engine='pyarrow', compression='gzip', index=False)


def model_region_year_total():
    print('\n* Create "region-year-total" file...')

    tmp_df = (
        df
        .groupby(['region', pd.Grouper(key='date',freq='Y'),'report'])['weaponcategory']
        .count()
        .reset_index()
        .rename(columns={'weaponcategory':'total'})
        .pivot_table(
            index=['region','date'],
            columns="report",
            values="total"
            )
        .assign(
            total = (
                df
                .groupby(['region', pd.Grouper(key='date',freq='Y')])['report']
                .count()
                .values
                )
            )
        .fillna(0)
        .reset_index()
        .astype({
            'region':'string',
            'date':'datetime64[ns]',
            'Loss':'int32',
            'Theft':'int32',
            'total':'int32'
            })
        .rename(columns={
            'Loss':'loss',
            'Theft':'theft'
            })   
        )
    
    tmp_df = (
        tmp_df
        .assign(loss_pct=tmp_df['loss']/tmp_df['total'])
        .assign(theft_pct=tmp_df['theft']/tmp_df['total'])
        .assign(total_pct=tmp_df['total']/tmp_df['total'].sum())
        .astype({
            'loss_pct':'float32',
            'theft_pct':'float32',
            'total_pct':'float32'
            })
        )


    print('File created')
    tmp_df.to_parquet('assets/models/region-year-total.parquet.gzip', engine='pyarrow', compression='gzip', index=False)
   

def model_region_weaponcategory_total():
    print('\n* Create "region-weaponcategory-total" file...') 

    tmp_df = (
        df
        .groupby(['region','weaponcategory'])['report']
        .count()
        .reset_index()
        .rename(columns={'report':'total'})
        .astype({
            'region':'string',
            'weaponcategory':'string',
            'total':'int32'
            })
        .fillna(0)
        )

    # Exclude weapon categories with no records in their respective region
    #tmp_df = tmp_df[tmp_df['total']!=0]

    tmp_df = (
        tmp_df
        # Weapon categories ranks in their region
        # (Rank 1 == weapon with the largest number of records in a region)
        .assign(
            local_rank=(
                tmp_df
                .groupby(['region'])['total']
                .rank(method='dense', ascending=False)
                .astype('int16')
                )
            )
        # Regional weapon categories ranks among all other regions in the country 
        # (Rank 1 == weapon category of a specific region has the largest number of records in the country)
        .assign(
            country_rank=(
                tmp_df['total']
                .rank(method='dense', ascending=False)
                .astype('int16')
                )
            )
        # Log (base 100) of each weapon category in every region 
        # (used for marker sizes in the scattertable visualisation)
        .assign(
            total_log100 = (np.log(tmp_df['total']) / np.log(100)).astype('float32')
            )
        # Total number of cases in the region
        .assign(
            total_region = (
                tmp_df
                .groupby(['region'])['total']
                .transform(sum)
                .astype('int32')
                )
            )
        # Total number of cases in the country
        .assign(
            total_country = (
                tmp_df['total']
                .sum()
                .astype('int64')
                )
            )
        .fillna(0)
        )

    print('File created')
    tmp_df.to_parquet('assets/models/region-weaponcategory-total.parquet.gzip', engine='pyarrow', compression='gzip', index=False)


def model_report_total():
    print('\n* Create "report-total" file...')

    tmp_df = (
        df
        .groupby('report')['date']
        .count()
        .reset_index()
        .rename(columns={'date':'total'})
        .astype({
            'report':'string',
            'total':'int32'
            })
        )

    print('File created\n')
    tmp_df.to_parquet('assets/models/report-total.parquet.gzip', engine='pyarrow', compression='gzip', index=True)


if __name__=='__main__':

    df = import_data()
    assert df.columns.isin(['date','region','report','weaponcategory']).all(), "DataFrame should have the following columns: 'date', 'region', 'report', 'weaponcategory'. Check pipeline."

    model_month_total()
    model_date_report_total()
    model_weaponcategory_total()
    model_region_total()
    model_region_year_total()
    model_region_weaponcategory_total()
    model_report_total()

    print('Finished running the script\n✅ Models successfuly created\n')
    

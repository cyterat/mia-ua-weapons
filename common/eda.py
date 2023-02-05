import pandas as pd
import numpy as np
from matplotlib.cbook import boxplot_stats

# aggregator()
def aggregator(df, frequency='Y', pivot=False):
    """
    Returns DataFrame grouped by specified date frequency.

    Parameters
    ----------
        df: pandas.core.frame.DataFrame
            Input DataFrame should have the following structure:

                     date| region| report| weaponcategory|
            0 |1991-08-26|   Lviv|  Theft|       Handguns|

        frequency: str (case-sensitive, default: 'Y' (year))
            Possible values: 'Y', 'Q', 'M', 'D', 'YrMo', 'Yr', 'Mo', 'DoM', 'DoW'.
            Other pandas offset aliases can be used (if applicable): 
            https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases

        pivot: boolean (default: False)
            Applies pivoting to 'report' column.

    Returns
    -------
        df: pandas DataFrame
    """
    pd.reset_option('^display.', silent=True)
    pd.options.display.float_format = '{:.6f}'.format
    
    # fmt: off
    df_dates = df.copy()
    df_dates = (
        df_dates
        .assign(YrMo=df_dates["date"].dt.to_period("M"))
        .assign(Yr=df_dates["date"].dt.year)
        .assign(Mo=df_dates["date"].dt.month)
        .assign(DoM=df_dates["date"].dt.day)
        .assign(DoW=df_dates["date"].dt.isocalendar().day # returns DoW from a tuple (year,week,day) where 1=Monday and 7=Sunday
        )  
    )

    if frequency in ["YrMo", "Yr", "Mo", "DoM", "DoW"]:
        date_part = date_name = frequency
    else:
        date_part = pd.Grouper(key="date", freq=frequency)
        date_name = 'date'

    grouped_df = (
        df_dates
        .pipe(lambda df_dates: df_dates.groupby([date_part, "region", "weaponcategory", "report"]).size())
        .pipe(lambda df_dates: df_dates.reset_index(name="frequency"))
        .pipe(lambda df_dates: df_dates.fillna(0))
        .pipe(lambda df_dates: df_dates.astype({"frequency": "int32"}))
        .pipe(lambda df_dates: df_dates[df_dates["frequency"]!=0])
        .pipe(lambda df_dates: df_dates.reset_index(drop=True))
    )
    
    if pivot:
        pivoted_df =(
            grouped_df
            .pipe(lambda grouped_df: grouped_df.pivot_table(index=[date_name, "region", "weaponcategory"], columns="report", values="frequency"))
            .pipe(lambda grouped_df: grouped_df.fillna(0))
            .pipe(lambda grouped_df: grouped_df.reset_index())
            .pipe(lambda grouped_df: grouped_df.astype({"Loss": "int32", "Theft": "int32"}))
            .pipe(lambda grouped_df: grouped_df.assign(frequency= grouped_df["Loss"] + grouped_df["Theft"]))
            .pipe(lambda grouped_df: grouped_df.rename(columns={"Loss": "loss", "Theft": "theft"}))
            .pipe(lambda grouped_df: grouped_df.assign(pct_of_total= grouped_df["frequency"] / np.sum(grouped_df["frequency"])))
            .pipe(lambda grouped_df: grouped_df.rename_axis(columns={"report": None}))
        )
        return pivoted_df
    else:
        return grouped_df
    

#country_stats
def country_stats(df,styler=False):
    """
    Returns DataFrame with summary information for each region.

    Parameters
    ----------
        df: aggregator(df, pivot=True)

    Returns
    -------
        df: pandas DataFrame

    Example
    -------
        Input:
                 date| region| report| weaponcategory|
        0 |1991-08-26|   Lviv|  Theft|       Handguns|

    \/      \/      \/      \/      \/      \/      \/      \/

        Output:
              region| theft| loss| theftRel| lossRel| frequency| pct_of_total|
        0 |Vinnytsia|   538| 4913|     0.10|    0.90|      5451|         0.03|
    """
    pd.reset_option('^display.', silent=True)
    pd.options.display.float_format = '{:.4f}'.format
    
    grouped = df.groupby(["region"])[['loss','theft','frequency','pct_of_total']].sum(numeric_only=True).reset_index().copy()

    #Adding percentages columns
    grouped["theft_pct"] = grouped["theft"] / grouped["frequency"]
    grouped["loss_pct"] = grouped["loss"] / grouped["frequency"]

    #Rearranging columns and sorting by "frequency"
    country_df = grouped.loc[:,["region","theft","loss","theft_pct","loss_pct","frequency","pct_of_total"]]
    country_df = (
        country_df
        .sort_values(by="frequency", ascending=False, ignore_index=True)
    )
    # fmt: off
    #Whether to apply the 'conditional' background color (if True returns Styler object)
    if styler==False:
        return country_df.round(4)
    elif styler==True:
        format_style={'theft_pct': '{:.2%}','loss_pct': '{:.2%}','pct_of_total': '{:.2%}'}
        #Configuring gradient thresholds for each column (uses https://matplotlib.org/3.1.1/api/cbook_api.html#matplotlib.cbook.boxplot_stats)
        return (
            country_df.round(4)
            .style
            .background_gradient(
                subset=['theft'],
                cmap="Blues", 
                vmin=float(boxplot_stats(country_df['theft'], whis=1.5)[0]['whislo']),
                vmax=float(boxplot_stats(country_df['theft'], whis=1.5)[0]['whishi'])
                )
            .background_gradient(
                subset=['loss'],
                cmap="Blues", 
                vmin=float(boxplot_stats(country_df['loss'], whis=1.5)[0]['whislo']),
                vmax=float(boxplot_stats(country_df['loss'], whis=1.5)[0]['whishi'])
                )
            .background_gradient(
                subset=['theft_pct'],
                cmap="Blues", 
                vmin=float(0),
                vmax=float(boxplot_stats(country_df['theft_pct'], whis=1.5)[0]['whishi'])
                ).format(precision=2)
            .background_gradient(
                subset=['loss_pct'],
                cmap="Blues",
                vmin=float(0),
                vmax=float(boxplot_stats(country_df['loss_pct'], whis=1.5)[0]['whishi'])
                ).format(precision=2)
            .background_gradient(
                subset=['frequency'],
                cmap="Blues", 
                vmin=float(boxplot_stats(country_df['frequency'], whis=1.5)[0]['whislo']),
                vmax=float(boxplot_stats(country_df['frequency'], whis=1.5)[0]['whishi'])
                )
            .background_gradient(
                subset=['pct_of_total'],
                cmap="Blues", 
                vmin=float(0),
                vmax=float(boxplot_stats(country_df['pct_of_total'], whis=1.5)[0]['whishi'])
                ).format(precision=4)
            .format(format_style).hide(axis="index")
            )
    else: 
        raise ValueError(f'Expected type boolean, got {type(styler)}.')
    
    
#region_stats
def region_stats(df, region, frequency='Y', styler=False):
    '''
    Generates summary stats DataFrame for a region grouped by frequency.
    
    Parameters
    ----------
        df: pandas.core.frame.DataFrame
        region: str
            Regional center name.
        frequency: str (case-sensitive, 'year' by default)
            Possible values: 'Y', 'Q', 'M', 'D', 'YrMo', 'Yr', 'Mo', 'DoM', 'DoW', 'We'.
            Other pandas offset aliases can be used (if applicable) as well. (https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases)
    Returns
    -------
        df: pandas DataFrame

     Example
    -------
        Input:
                 date| region| report| weaponcategory|
        0 |1991-08-26|   Lviv|  Theft|       Handguns|

    \/      \/      \/      \/      \/      \/      \/      \/

        Output:
                 date| loss| theft| frequency| pct_of_total| frequencyD|   relD|
        0 |1991-12-31|    0|     1|         1|       0.0010|          0| 0.0000|
    '''
    pd.reset_option('^display.', silent=True)
    pd.options.display.float_format = '{:.4f}'.format
    
    # fmt: off
    df_dates = df.copy()
    df_dates = (
        df_dates
        .assign(YrMo=df_dates["date"].dt.to_period("M")) #year & month
        .assign(Yr=df_dates["date"].dt.year) #year
        .assign(Mo=df_dates["date"].dt.month) #month of year
        .assign(DoM=df_dates["date"].dt.day) #day of month
        .assign(DoW=df_dates["date"].dt.isocalendar().day)  # returns DoW from a tuple (year,week,day) where 1=Monday and 7=Sunday
        .assign(We=df_dates["date"].dt.isocalendar().week) #week of year
        )

    if frequency in ["YrMo", "Yr", "Mo", "DoM", "DoW", "We"]:
        date_part = frequency
    else:
        date_part = pd.Grouper(key = "date", freq = frequency)

    #Filtering specific region
    filtered_df = df_dates[df_dates["region"]==region]
    
    #Grouping filtered_df by specified frequency
    grouped_df = (
        filtered_df
        .groupby([date_part, "report"])
        .size()
        .reset_index(name = "frequency")
        )
    
    #Reshaping grouped_df to pivot table format 
    pivoted_df = (
        grouped_df
        .rename(columns = {"report": region})
        .pivot(index = grouped_df.columns[0], columns = region, values = "frequency")
        .reset_index()
        .rename(columns = {"Loss":"loss", "Theft":"theft"})
        )
    
    #Casting DataFrame columns to int data type
    base_df = (
        pivoted_df
        .pipe(lambda pivoted_df: pivoted_df.astype(dict.fromkeys(["loss", "theft"], "int32")))
        .pipe(lambda pivoted_df: pivoted_df.assign(frequency = pivoted_df["loss"] + pivoted_df["theft"]))
        .pipe(lambda pivoted_df: pivoted_df.assign(pct_of_total= pivoted_df["frequency"] / np.sum(pivoted_df["frequency"])))
        )
    
    #Adding calculated columns
    extended_df = (
        base_df
        .assign(frequencyD = base_df["frequency"].diff().fillna(0).astype('int'))
        .assign(
            relD = base_df["pct_of_total"].diff()
            #relD = base_df["frequency"].pct_change()
            )
        .replace([np.inf, -np.inf, np.nan], 0)
        )
    
    #Whether to apply the 'conditional' background color (if True returns Styler object)
    if styler==False:
        return extended_df.round(4)
    elif styler==True:
        format_style={'pct_of_total': '{:.2%}','relD': '{:.2%}'}
        #Configuring gradient thresholds for each column (uses https://matplotlib.org/3.1.1/api/cbook_api.html#matplotlib.cbook.boxplot_stats)
        return (
            extended_df.round(4)
            .style
            .background_gradient(
                subset=['loss'],
                cmap="Blues", 
                vmin=int(boxplot_stats(extended_df['loss'], whis=1.5)[0]['whislo']),
                vmax=int(boxplot_stats(extended_df['loss'], whis=1.5)[0]['whishi'])
                )
            .background_gradient(
                subset=['theft'],
                cmap="Blues", 
                vmin=int(boxplot_stats(extended_df['theft'], whis=1.5)[0]['whislo']),
                vmax=int(boxplot_stats(extended_df['theft'], whis=1.5)[0]['whishi'])
                )
            .background_gradient(
                subset=['frequency'],
                cmap="Blues", 
                vmin=int(boxplot_stats(extended_df['frequency'], whis=1.5)[0]['whislo']),
                vmax=int(boxplot_stats(extended_df['frequency'], whis=1.5)[0]['whishi'])
                )
            .background_gradient(
                subset=['pct_of_total'],
                cmap="Blues",
                vmin=float(0),
                vmax=float(boxplot_stats(extended_df['pct_of_total'], whis=1.5)[0]['whishi'])
                ).format(precision=3)
            .background_gradient(
                subset=['frequencyD'],
                cmap="Blues",
                vmin=int(0),
                vmax=int(boxplot_stats(extended_df['frequencyD'], whis=1.5)[0]['whishi'])
                )
            .background_gradient(
                subset=['relD'],
                cmap="Blues",
                vmin=float(0),
                vmax=float(boxplot_stats(extended_df['relD'], whis=1.5)[0]['whishi'])
                ).format(precision=3)
            .format(format_style).hide(axis="index")
            )
    else: 
        raise ValueError(f'Expected boolean, got {type(styler)}.')

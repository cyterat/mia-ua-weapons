import streamlit as st
import pandas as pd
from pandas.tseries.offsets import MonthEnd
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio

def generate_events_barchart():
    
    # Data
    df = pd.read_parquet('assets/models/month-total.parquet.gzip')
    
    # Colors
    clr_tile_background = '#292929'
    clr_page_background = '#333333'
    clr_hoverlabel = 'rgba(51, 51, 51, 0.95)' #333333, opacity 0.95
    clr_arrow = '#8d9294'
    
    clr_transparent = 'rgba(0,0,0,0)'
    clr_semi_transparent = 'rgba(0,0,0,0.5)'
    
    clr_bar = '#dedede'
    clr_bar_event = '#26c8cd'
    clr_bar_outlier = '#e54848'
    
    # Font
    font_family = 'Montserrat, sans-serif'
    clr_font = '#dedede'
    clr_secondary_font = '#8d9294'
    
    # Other
    arrowline_xshift = '-28' # ensures arrow is approx. in the middle of the bar (basically adds 28 days)
    
    # Outlier condition (also used in annotation text, therefore not 0.0 but 0.00 format)
    threshold = 0.90
    
    # # V1 Conditional bar color
    # cnd_clr = (df['total'] >= df['total'].quantile(threshold)).astype('int')
    # cnd_clr_map = [
    #     [0, clr_bar], # below threshold
    #     [1, clr_bar_outlier] # above threshold
    #     ]
    
    # V2 Conditional bar color
    cnd_event_list = pd.to_datetime(['1991-08', '1994-07', '1999-11', '2000-11', '2004-11', '2005-01', '2008-09', '2010-02', '2013-11', '2014-03', '2014-06', '2015-07', '2017-03', '2019-05', '2022-02']) + MonthEnd(0) 
    
    cnd_clr = pd.Series(
        np.where(
            df['total'] >= df['total'].quantile(threshold),
            'outlier', # 1st priority
            np.where(
                df['date'].isin(cnd_event_list),
                'event',  # 2nd priority
                'normal' # 3rd priority
            )
        )
    ).astype(str).map({
        'outlier':1, 
        'event':0.5, 
        'normal':0
    })

    cnd_clr_map = [
        [0, clr_bar],
        [0.5, clr_bar_event], 
        [1, clr_bar_outlier]
        ]


    # Chart
    fig = go.Figure()
    fig.add_bar(
        x=df['date'],
        y=df['total'],
        hovertemplate='%{x|%B}<br>%{y:,} records<extra></extra>',
        marker={
            'color':cnd_clr,
            'colorscale':cnd_clr_map,
            'line_width':0
            }
        )

    # Annotations
    fig.add_annotation(
        x='1991-08' + arrowline_xshift,
        y=df[df['date'].astype(str).str.contains('1991-08')][
            'total'
        ].iloc[0],
        text=f"<a style='color:{clr_font}' href='https://en.wikipedia.org/wiki/Declaration_of_Independence_of_Ukraine'>Ukraine Declares <span style='color: {clr_bar_event}'><b>Independence</b></span></a><br><a style='color:{clr_font}' href='https://en.wikipedia.org/wiki/Leonid_Kravchuk'><span style='color: {clr_bar_event}'><b>Leonid Kravchuk</b></span><br>becomes president</a>",
        align='left',
        showarrow=True,
        yanchor='bottom',
        yshift=5,
        arrowhead=0,
        arrowsize=2,
        arrowwidth=1,
        arrowcolor=clr_arrow,
        ax=45,
        ay=-105,
    )

    fig.add_annotation(
        x='1994-07' + arrowline_xshift,
        y=df[df['date'].astype(str).str.contains('1994-07')][
            'total'
        ].iloc[0],
        text=f"<a style='color:{clr_font}' href='https://en.wikipedia.org/wiki/Leonid_Kuchma'><span style='color: {clr_bar_event}'><b>Leonid Kuchma</b></span><br>becomes president</a>",
        align='left',
        showarrow=True,
        yanchor='bottom',
        yshift=5,
        arrowhead=0,
        arrowsize=2,
        arrowwidth=1,
        arrowcolor=clr_arrow,
        ax=30,
        ay=-35,
    )

    fig.add_annotation(
        x='1999-11' + arrowline_xshift,
        y=df[df['date'].astype(str).str.contains('1999-11')][
            'total'
        ].iloc[0],
        text=f"<a style='color:{clr_font}' href='https://en.wikipedia.org/wiki/Leonid_Kuchma'><span style='color: {clr_bar_event}'><b>Leonid Kuchma</b></span><br>re-elected<br>for <span style='color: {clr_bar_event}'><b>second term</b></span></a>",
        align='left',
        showarrow=True,
        yanchor='bottom',
        yshift=5,
        arrowhead=0,
        arrowsize=2,
        arrowwidth=1,
        arrowcolor=clr_arrow,
        ax=-45,
        ay=-110,  # arrow length
    )

    fig.add_annotation(
        x='2000-11' + arrowline_xshift,
        y=df[df['date'].astype(str).str.contains('2000-11')][
            'total'
        ].iloc[0],
        text=f"<a style='color:{clr_font}' href='https://en.wikipedia.org/wiki/Cassette_Scandal'>The Cassette <b><span style='color: {clr_bar_event}'>Scandal</b></span></a>",
        align='left',
        showarrow=True,
        yanchor='bottom',
        yshift=5,
        arrowhead=0,
        arrowsize=2,
        arrowwidth=1,
        arrowcolor=clr_arrow,
        ax=35,
        ay=-15,
    )

    fig.add_annotation(
        x='2004-11' + arrowline_xshift,
        y=df[df['date'].astype(str).str.contains('2004-11')][
            'total'
        ].iloc[0],
        text=f"<a style='color:{clr_font}' href='https://en.wikipedia.org/wiki/Orange_Revolution'>Orange<br><span style='color: {clr_bar_event}'><b>Revolution</b></span></a>",
        align='left',
        showarrow=True,
        yanchor='bottom',
        yshift=5,
        arrowhead=0,
        arrowsize=2,
        arrowwidth=1,
        arrowcolor=clr_arrow,
        ax=-30,
        ay=-50,
    )

    fig.add_annotation(
        x='2005-01' + arrowline_xshift,
        y=df[df['date'].astype(str).str.contains('2005-01')][
            'total'
        ].iloc[0],
        text=f"<a style='color:{clr_font}' href='https://en.wikipedia.org/wiki/Viktor_Yushchenko'><span style='color: {clr_bar_event}'><b>Viktor Yushchenko</b></span><br>becomes president</a>",
        align='left',
        showarrow=True,
        yanchor='bottom',
        yshift=5,
        arrowhead=0,
        arrowsize=2,
        arrowwidth=1,
        arrowcolor=clr_arrow,
        ax=30,
        ay=-110,
    )

    fig.add_annotation(
        x='2008-09' + arrowline_xshift,
        y=df[df['date'].astype(str).str.contains('2008-09')][
            'total'
        ].iloc[0],
        text=f"<a style='color:{clr_font}' href='https://en.wikipedia.org/wiki/2007%E2%80%932008_financial_crisis'>Global <span style='color: {clr_bar_event}'><b>Financial Crisis</b></span><br>reaches its climax</a>",
        align='left',
        showarrow=True,
        yanchor='bottom',
        yshift=5,
        arrowhead=0,
        arrowsize=2,
        arrowwidth=1,
        arrowcolor=clr_arrow,
        ax=0,
        ay=-160,
    )

    fig.add_annotation(
        x='2010-02' + arrowline_xshift,
        y=df[df['date'].astype(str).str.contains('2010-02')][
            'total'
        ].iloc[0],
        text=f"<a style='color:{clr_font}' href='https://en.wikipedia.org/wiki/Viktor_Yanukovych'><span style='color: {clr_bar_event}'><b>Viktor Yanukovych</b></span><br>becomes president</a>",
        align='left',
        showarrow=True,
        yanchor='bottom',
        yshift=5,
        arrowhead=0,
        arrowsize=2,
        arrowwidth=1,
        arrowcolor=clr_arrow,
        ax=30,
        ay=-70,
    )

    fig.add_annotation(
        x='2013-11' + arrowline_xshift,
        y=df[df['date'].astype(str).str.contains('2013-11')][
            'total'
        ].iloc[0],
        text=f"<a style='color:{clr_font}' href='https://en.wikipedia.org/wiki/Euromaidan'><span style='color: {clr_bar_event}'><b>Euromaidan</b></span><br>protests</a>",
        align='left',
        showarrow=True,
        yanchor='bottom',
        yshift=5,
        arrowhead=0,
        arrowsize=2,
        arrowwidth=1,
        arrowcolor=clr_arrow,
        ax=-45,
        ay=-15,
    )

    fig.add_annotation(
        x='2014-03' + arrowline_xshift,
        y=df[df['date'].astype(str).str.contains('2014-03')][
            'total'
        ].iloc[0],
        text=f"<a style='color:{clr_font}' href='https://en.wikipedia.org/wiki/Russo-Ukrainian_War'>Russo-Ukrainian <span style='color: {clr_bar_event}'><b>War</b></span></a>",
        align='left',
        showarrow=True,
        yanchor='bottom',
        yshift=5,
        arrowhead=0,
        arrowsize=2,
        arrowwidth=1,
        arrowcolor=clr_arrow,
        ax=0,
        ay=-20,
    )
    
    fig.add_annotation(
        x='2014-06' + arrowline_xshift,
        y=df[df['date'].astype(str).str.contains('2014-06')][
            'total'
        ].iloc[0],
        text=f"<a style='color:{clr_font}' href='https://en.wikipedia.org/wiki/Petro_Poroshenko'><span style='color: {clr_bar_event}'><b>Petro<br>Poroshenko</b></span><br>becomes<br>president</a>",
        align='left',
        showarrow=True,
        yanchor='bottom',
        yshift=5,
        xanchor='left',
        arrowhead=0,
        arrowsize=2,
        arrowwidth=1,
        arrowcolor=clr_arrow,
        ax=20,
        ay=-300,
    )

    fig.add_annotation(
        x='2015-07' + arrowline_xshift,
        y=df[df['date'].astype(str).str.contains('2015-07')][
            'total'
        ].iloc[0],
        text=f"<a style='color:{clr_font}' href='https://en.wikipedia.org/wiki/National_Police_of_Ukraine'>Large-scale<br><span style='color: {clr_bar_event}'><b>police<br>reforms</b></span></a>",
        align='left',
        showarrow=True,
        yanchor='bottom',
        yshift=5,
        arrowhead=0,
        arrowsize=2,
        arrowwidth=1,
        arrowcolor=clr_arrow,
        ax=7,
        ay=-45,
    )

    fig.add_annotation(
        x='2017-03' + arrowline_xshift,
        y=df[df['date'].astype(str).str.contains('2017-03')][
            'total'
        ].iloc[0],
        text="???",
        showarrow=True,
        yanchor='bottom',
        yshift=5,
        arrowhead=0,
        arrowsize=2,
        arrowwidth=1,
        arrowcolor=clr_arrow,
        ax=0,
        ay=-20,
    )

    fig.add_annotation(
        x='2019-05' + arrowline_xshift,
        y=df[df['date'].astype(str).str.contains('2019-05')][
            'total'
        ].iloc[0],
        text=f"<a style='color:{clr_font}' href='https://en.wikipedia.org/wiki/Volodymyr_Zelenskyy'><span style='color: {clr_bar_event}'><b>Volodymyr <br>Zelenskyy</b></span><br>becomes <br>president</a>",
        align='left',
        showarrow=True,
        yanchor='bottom',
        yshift=5,
        arrowhead=0,
        arrowsize=2,
        arrowwidth=1,
        arrowcolor=clr_arrow,
        ax=0,
        ay=-30,
    )

    fig.add_annotation(
        x='2022-02' + arrowline_xshift,
        y=df[df['date'].astype(str).str.contains('2022-02')][
            'total'
        ].iloc[0],
        text=f"<a style='color:{clr_font}' href='https://en.wikipedia.org/wiki/Russian_invasion_of_Ukraine'>Russian<br><span style='color: {clr_bar_event}'><b>full-scale invasion</b></span><br>of Ukraine</a>",
        align='left',
        showarrow=True,
        yanchor='bottom',
        yshift=5,
        arrowhead=0,
        arrowsize=2,
        arrowwidth=1,
        arrowcolor=clr_arrow,
        ax=0,
        ay=-85,
    )
    
    # Events barchart title
    fig.add_annotation(
        x=df['date'].quantile(0.199),
        y=df['total'].max() / 1.5,
        text=f"""
        <span style='color: {clr_bar}; font-size:25px'><b>Monthly totals</b></span>
        <br></br>
        <span style='color: {clr_font}; font-size:25px'>of lost and stolen weapons</span>
        <br></br>
        <span style='color: {clr_font}; font-size:25px'>throughout the <span style='color: {clr_bar_event}; font-size:25px'><b>modern history of Ukraine<b></span></span>
        """,
        align='left',
        showarrow=False,
        yanchor='bottom',
    )
    
    # Note
    fig.add_annotation(
        x=df['date'].quantile(0.1975),
        y=df['total'].max() / 1.7,
        text=f"""
        <span style='color: {clr_secondary_font}; font-size:12px;'>Note: Events (clickable) on the visualization are time markers and may not be the main contributors</span><br>
        <span style='color: {clr_secondary_font}; font-size:12px;'>to the total monthly number of records.</span>
        """,
        align='left',
        showarrow=False,
        yanchor='bottom',
    )
    
    # Events barchart title
    fig.add_annotation(
        x=df['date'].quantile(0.9, interpolation='nearest'),
        y=df['total'].max() / 1.25,
        text=f"<span style='font-size:15px; color:{clr_font}'>From 2014 onwards,<br>a <span style='color:{clr_bar_outlier}'><b>notable shift</b></span> occurs<br>as the recorded monthly totals<br>repeatedly exceed<br><span style='color:{clr_bar_outlier}'><b>the {int(threshold*100)}th percentile</b></span></span>",
        align='left',
        showarrow=False,
        yanchor='bottom',
    )
    
    # Events barchart info annotation
    fig.add_annotation(
        xref='paper',
        yref='paper',
        x=-0.025,
        y=-0.0575,
        yanchor='top',
        showarrow=False,
        align='left',
        text=f"""
        <span style='color: {clr_secondary_font}; font-size:12px'>
        Data Source: MIA of Ukraine ⋅ Visualization by: cyterat ⋅ Available at: https://ua-weapons.streamlit.app ⋅ Year: {df['date'].dt.year.max()}
        </span><br>
        <a style='color:{clr_secondary_font}; font-size:12px' href='https://raw.githubusercontent.com/cyterat/mia-ua-weapons-v2/main/assets/ua-weapons-history.png'>
        Click <b>here</b> to open png format of this visualization
        </span></a>
        """,
    )

    fig.update_layout(
        height=680,
        width=1900,
        bargroupgap=0.1,
        barmode='group',
        margin={
            'l':20, 
            'r':0,
            't':20, 
            'b':80
            },
        font_color=clr_font,
        font_size=14,
        font_family=font_family,
        showlegend=False,
        xaxis={
            'title':None,
            'gridcolor':clr_transparent,
            'tickmode':'array',
            'tickvals':df['date'].dt.year.to_list(),
            'tickformat':'%Y',
            'tickfont_size':12,
            'tickfont_color':clr_secondary_font,
            'spikecolor':clr_semi_transparent,
            'spikethickness':1
            },
        yaxis={
            'title':None,
            'showticklabels':False,
            'gridcolor':clr_transparent,
            'zerolinecolor':clr_transparent
            },
        hovermode='x unified',
        hoverlabel={
            'bgcolor':clr_hoverlabel,
            'font_color':clr_font,
            'font_family':font_family,
            'font_size':13
            },
        modebar={
            'orientation':'h',
            'bgcolor':clr_transparent,
            'color':clr_bar_event
            },
        )

    # Add vertical greyed out rectangles representing years span
    for year in range(1991, max(df['date'].dt.year)+1, 2):
        fig.add_vrect(
            x0=str(year),
            x1=str(year + 1),
            y0=-1,
            y1=10,
            line_width=0,
            fillcolor=clr_page_background,
            opacity=0.1,
            layer='below',
        )

    # Add watermark
    fig.add_layout_image(
        {
            'source':'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAzIiBoZWlnaHQ9IjI5MSIgdmlld0JveD0iMCAwIDMwMyAyOTEiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnIGZpbHRlcj0idXJsKCNmaWx0ZXIwX2RfMV8yMikiPgo8cGF0aCBkPSJNMTA2LjAwMSA3My43OTE4SDE5NC40MjNNMTk0LjQyMyA3My43OTE4VjE1OS45NDFNMTk0LjQyMyA3My43OTE4TDE2Mi4wMDIgMTEwLjE2Nk0xOTQuNDIzIDE1OS45NDFMMjUwIDIxNC4wODlNMTk0LjQyMyAxNTkuOTQxTDE2MS4wMTkgMTk3LjI3Mk03My41NzkzIDExMC4xNjZIMTYyLjAwMk0xNjIuMDAyIDExMC4xNjZWMTk2LjMxNU03Mi41OTY4IDE5Ny4yNzJIMTYxLjAxOU0xNjEuMDE5IDE5Ny4yNzJMMTg3LjkwMSAyNjkuMjMxTTE5NC40MjMgNzMuMzc4OEwyNTAgMTkuMjMwOE01MCAxOS4yMzA4TDEwNS41NzcgNzMuMzc4OCIgc3Ryb2tlPSIjMEZCQkUxIiBzdHJva2Utd2lkdGg9IjIxIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHNoYXBlLXJlbmRlcmluZz0iY3Jpc3BFZGdlcyIvPgo8L2c+CjxwYXRoIGQ9Ik0xNjIuMDAyIDExMC4xNjZMMTk0LjQyMyA3My43OTE4VjE2MC44OThMMTYyLjAwMiAxOTkuMTg2VjExMC4xNjZaIiBmaWxsPSIjMEZCQkUxIi8+CjxkZWZzPgo8ZmlsdGVyIGlkPSJmaWx0ZXIwX2RfMV8yMiIgeD0iMzUuNSIgeT0iOC43MzA3NiIgd2lkdGg9IjIyOSIgaGVpZ2h0PSIyNzkuMDAzIiBmaWx0ZXJVbml0cz0idXNlclNwYWNlT25Vc2UiIGNvbG9yLWludGVycG9sYXRpb24tZmlsdGVycz0ic1JHQiI+CjxmZUZsb29kIGZsb29kLW9wYWNpdHk9IjAiIHJlc3VsdD0iQmFja2dyb3VuZEltYWdlRml4Ii8+CjxmZUNvbG9yTWF0cml4IGluPSJTb3VyY2VBbHBoYSIgdHlwZT0ibWF0cml4IiB2YWx1ZXM9IjAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDEyNyAwIiByZXN1bHQ9ImhhcmRBbHBoYSIvPgo8ZmVPZmZzZXQgZHk9IjQiLz4KPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMiIvPgo8ZmVDb21wb3NpdGUgaW4yPSJoYXJkQWxwaGEiIG9wZXJhdG9yPSJvdXQiLz4KPGZlQ29sb3JNYXRyaXggdHlwZT0ibWF0cml4IiB2YWx1ZXM9IjAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAuMjUgMCIvPgo8ZmVCbGVuZCBtb2RlPSJub3JtYWwiIGluMj0iQmFja2dyb3VuZEltYWdlRml4IiByZXN1bHQ9ImVmZmVjdDFfZHJvcFNoYWRvd18xXzIyIi8+CjxmZUJsZW5kIG1vZGU9Im5vcm1hbCIgaW49IlNvdXJjZUdyYXBoaWMiIGluMj0iZWZmZWN0MV9kcm9wU2hhZG93XzFfMjIiIHJlc3VsdD0ic2hhcGUiLz4KPC9maWx0ZXI+CjwvZGVmcz4KPC9zdmc+Cg==',
            'x':0.2,
            'y':0.75,
            'sizex':0.6,
            'sizey':0.6,
            'sizing':'contain',
            'opacity':0.02,
            'layer':'above',
        }
    )

    # Disable chart "zoom in" and "zoom out"
    fig.layout.xaxis.fixedrange = False
    fig.layout.yaxis.fixedrange = True

    # Hide options bar above the chart
    # config = {'displayModeBar': False}
    
    config = {
        'displaylogo': False,
        'modeBarButtonsToRemove': [
            'select2d',
            'lasso2d',
            'autoScale2d',
            'zoomIn2d',
            'zoomOut2d',
            'toImage',
            ]
        }
    
    # Export the figure to a PNG file with the specified background color
    fig.update_layout(
        plot_bgcolor=clr_tile_background,
        paper_bgcolor=clr_tile_background
    )

    pio.write_image(fig, f'assets/ua-weapons-history.png', format='png', width=1900, height=680)

    # Reset the background color to transparent for display
    fig.update_layout(
        plot_bgcolor=clr_tile_background,  
        paper_bgcolor=clr_transparent
    )

    return st.plotly_chart(fig, config=config, use_container_width=True)
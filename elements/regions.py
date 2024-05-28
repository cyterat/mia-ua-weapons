import streamlit as st
import os.path, time
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Data
region_total = pd.read_parquet("assets/models/region-total.parquet.gzip")
region_year_total = pd.read_parquet("assets/models/region-year-total.parquet.gzip")
population = pd.read_csv("assets/ua-population.csv", usecols=["region", "2020", "2021"])


# File modification year
def modification_date(file):
    t = os.path.getmtime(file)
    year, month, day, hour, minute, second = time.localtime(t)[:-3]
    date = f"{year}"
    return date


# Colors
clr = "#00ccd3"
biclr = ["#faffff", "#007a81"]

# Colors
clr_main = '#2dcdd2'
clr_font = '#dedede'
clr_secondary_font = '#8d9294'

clr_page_background = '#333333'
clr_tile_background = '#262626'
clr_hoverlabel = 'rgba(51, 51, 51, 0.95)'
clr_transparent = 'rgba(0,0,0,0)'

clr_button_background = '#8d9294' 
clr_button_text = '#292929'

clr_loss = '#679496'
clr_theft = '#006C72'
clr_outlier = '#e54848'

# Font
font_main = 'Montserrat, sans-serif'

watermark = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAzIiBoZWlnaHQ9IjI5MSIgdmlld0JveD0iMCAwIDMwMyAyOTEiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxnIGZpbHRlcj0idXJsKCNmaWx0ZXIwX2RfMV8yMikiPgo8cGF0aCBkPSJNMTA2LjAwMSA3My43OTE4SDE5NC40MjNNMTk0LjQyMyA3My43OTE4VjE1OS45NDFNMTk0LjQyMyA3My43OTE4TDE2Mi4wMDIgMTEwLjE2Nk0xOTQuNDIzIDE1OS45NDFMMjUwIDIxNC4wODlNMTk0LjQyMyAxNTkuOTQxTDE2MS4wMTkgMTk3LjI3Mk03My41NzkzIDExMC4xNjZIMTYyLjAwMk0xNjIuMDAyIDExMC4xNjZWMTk2LjMxNU03Mi41OTY4IDE5Ny4yNzJIMTYxLjAxOU0xNjEuMDE5IDE5Ny4yNzJMMTg3LjkwMSAyNjkuMjMxTTE5NC40MjMgNzMuMzc4OEwyNTAgMTkuMjMwOE01MCAxOS4yMzA4TDEwNS41NzcgNzMuMzc4OCIgc3Ryb2tlPSIjMEZCQkUxIiBzdHJva2Utd2lkdGg9IjIxIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHNoYXBlLXJlbmRlcmluZz0iY3Jpc3BFZGdlcyIvPgo8L2c+CjxwYXRoIGQ9Ik0xNjIuMDAyIDExMC4xNjZMMTk0LjQyMyA3My43OTE4VjE2MC44OThMMTYyLjAwMiAxOTkuMTg2VjExMC4xNjZaIiBmaWxsPSIjMEZCQkUxIi8+CjxkZWZzPgo8ZmlsdGVyIGlkPSJmaWx0ZXIwX2RfMV8yMiIgeD0iMzUuNSIgeT0iOC43MzA3NiIgd2lkdGg9IjIyOSIgaGVpZ2h0PSIyNzkuMDAzIiBmaWx0ZXJVbml0cz0idXNlclNwYWNlT25Vc2UiIGNvbG9yLWludGVycG9sYXRpb24tZmlsdGVycz0ic1JHQiI+CjxmZUZsb29kIGZsb29kLW9wYWNpdHk9IjAiIHJlc3VsdD0iQmFja2dyb3VuZEltYWdlRml4Ii8+CjxmZUNvbG9yTWF0cml4IGluPSJTb3VyY2VBbHBoYSIgdHlwZT0ibWF0cml4IiB2YWx1ZXM9IjAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDEyNyAwIiByZXN1bHQ9ImhhcmRBbHBoYSIvPgo8ZmVPZmZzZXQgZHk9IjQiLz4KPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMiIvPgo8ZmVDb21wb3NpdGUgaW4yPSJoYXJkQWxwaGEiIG9wZXJhdG9yPSJvdXQiLz4KPGZlQ29sb3JNYXRyaXggdHlwZT0ibWF0cml4IiB2YWx1ZXM9IjAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAgMCAwIDAuMjUgMCIvPgo8ZmVCbGVuZCBtb2RlPSJub3JtYWwiIGluMj0iQmFja2dyb3VuZEltYWdlRml4IiByZXN1bHQ9ImVmZmVjdDFfZHJvcFNoYWRvd18xXzIyIi8+CjxmZUJsZW5kIG1vZGU9Im5vcm1hbCIgaW49IlNvdXJjZUdyYXBoaWMiIGluMj0iZWZmZWN0MV9kcm9wU2hhZG93XzFfMjIiIHJlc3VsdD0ic2hhcGUiLz4KPC9maWx0ZXI+CjwvZGVmcz4KPC9zdmc+Cg=='


# Region, rank, population (1st 'column')
def generate_rank_region_population(region):
    rank = region_total[region_total['region'] == region].index[0] + 1
    pop = population.loc[population['region'] == region, '2021'].iloc[0]
    year = population.columns.tolist()[-1]
    return st.markdown(
        f"""
        <span style='font-size:30px; font-family:{font_main}; font-weight:700; line-height: 2rem;'>
            <span style='color:{clr_secondary_font}'>#{rank}</span> 
            <span style='color:{clr_font}'>{region.title()}</b></span><br>
            <span title='Population in {2021}' style='font-size:16px; color:{clr_secondary_font}; margin-bottom: 1rem;'>&#128578 {int(pop):,} <sup>?</sup></span>
        </span>""",
        unsafe_allow_html=True,
    )


# Yearly totals plotly chart
def generate_region_total_linechart(region):
    df = region_year_total[(region_year_total['region'] == str(region))]
    
    total = int(region_total[(region_total['region'] == region)]['total'])

    max = df['total'].max()
    
    yr_max = int(df.loc[df['total'] == max, 'date'].dt.year)

    htext = "%{y:,.0f} records<extra></extra>"

    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=df['date'].dt.year,
            y=df['total'],
            name='Total',
            line={
                'color':clr_font, 
                'width':4
                },
            mode='lines',
            hovertemplate=htext,
        )
    )
    
    # Max total
    fig.add_trace(
        go.Scatter(
            x=df[df['total']==df['total'].max()]['date'].dt.year,
            y=np.array(df['total'].max()),
            name='max',
            marker={
                'color':clr_outlier,
                'size':7
                },
            mode='markers',
            hoverinfo='skip'
        )
    )
    
    # Current number of records
    fig.add_trace(
        go.Scatter(
            x=df.tail(1)['date'].dt.year,
            y=np.array(int(df.tail(1)['total'])),
            name='current',
            marker={
                'color':clr_main,
                'size':7
                },
            mode='markers',
            hoverinfo='skip'
        )
    )
    
    # Settings
    fig.update_layout(
        height=160,
        width=420,
        plot_bgcolor=clr_tile_background,
        paper_bgcolor=clr_transparent,
        font_size=14,
        font_color=clr_font,
        margin={
            'l':5,
            'r':50, 
            't':30, 
            'b':5
            },
        showlegend=False,
        xaxis={
            'title':None,
            'showticklabels':True,
            'gridcolor':clr_page_background,
            'dtick':7,
            'tickformat':'%Y',
            'tickfont_size':12,
            'tickfont_family':font_main,
            'tickfont_color':clr_secondary_font,
        },
        yaxis={
            'title':None, 
            'showticklabels':True, 
            'gridcolor':clr_page_background, 
            'zeroline':False,
            'tickfont_size':12,
            'tickfont_family':font_main,
            'tickfont_color':clr_secondary_font,
        },
        hovermode='x unified',
        hoverlabel={
            'bgcolor':'rgba(72,72,72,0.8)',
            'font_color':clr_font
            },  
    )
    
    # Max total
    fig.add_annotation(
        xref='paper',
        yref='paper',
        x=0.08,
        y=0.9,
        xanchor='left',
        showarrow=False,
        align='left',
        text=f"Max:<br><span style='color: {clr_outlier}'>{max:,}</span><br>({yr_max})",
        font_family=font_main,
        font_size=13,
        font_color=clr_secondary_font
    )
    
    # Current number of records
    fig.add_annotation(
        xref='paper',
        x=0.95,
        y=np.array(int(df.tail(1)['total'])),
        xanchor='left',
        showarrow=False,
        align='left',
        text=f"<span style='color: {clr_main}'>{int(df.tail(1)['total']):,}</span>",
        font_family=font_main,
        font_size=13,
        font_color=clr_secondary_font
    )
    
    # Total records (title)
    fig.update_layout(
        title=f"<span style='font-size:14px; font-family:{font_main}; color: {clr_secondary_font}'>Total records: <span style='color: {clr_font}'>{total:,}</span></span>",
        title_x=0.25,
        )

    # Watermark
    fig.add_layout_image(
        {
            'source':watermark,
            'x':0.15,
            'y':0.85,
            'sizex':0.7,
            'sizey':0.7,
            'sizing':'contain',
            'opacity':0.05,
            'layer':'above',
        }
    )

    # Disable chart "zoom in" and "zoom out"
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True

    # Hide options bar above the chart
    config = {'displayModeBar': False}

    return st.plotly_chart(fig, config=config, use_container_width=True)


# Polar chart of weapon categories
def generate_region_weapons_polarchart(region):
    df = pd.read_parquet("assets/models/region-weaponcategory-total.parquet.gzip")
    
    df['rank'] = df.groupby('region')['total'].rank(method='dense', ascending=True).astype('int8')
    
    ranks_range = [0, df['rank'].max()]
    
    df = df.pivot(index='region',columns='weaponcategory', values='rank').fillna(0).astype('int8')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        hoveron='fills',
        r=df.loc[region,:].values.tolist() + df.loc[region,:].values.tolist()[:1],
        theta=df.columns.tolist() + df.columns.tolist()[:1],
        fillcolor=None,
        opacity=0.9,
        hovertemplate = None,
        hoverinfo = 'skip',
        fill='toself',
        name=region,
        mode='lines+markers',
        line={
            'color':clr_main,
            'width':3
            },
        marker={
            'color':clr_main,
            'size':6
            }
        ))

    fig.update_layout(
        paper_bgcolor=clr_transparent,
        plot_bgcolor=clr_tile_background,
        height=160,
        width=350,
        margin={
            'l':110, 
            'r':120, 
            't':25, 
            'b':25
            },
        polar={
            'bgcolor':clr_tile_background,
            'angularaxis':{
                'gridcolor':clr_page_background,
                'showline':False,
                'linecolor':clr_page_background,
            },
            'radialaxis':{
                'visible':True,
                'gridcolor':clr_page_background,
                'showticklabels':False,
                'showline':False,
                'layer':'below traces',
                'range': ranks_range
            }
        },
        font_family=font_main,
        font_color=clr_secondary_font,
        font_size=11,
        showlegend=False,
        dragmode=False
    )

    # Watermark
    fig.add_layout_image(
        {
            'source':watermark,
            'x':0.1,
            'y':0.85,
            'sizex':0.8,
            'sizey':0.8,
            'sizing':'contain',
            'opacity':.06,
            'layer':'above'
        }
    )

    # Hide options bar above the chart
    config = {'displayModeBar': False}

    return st.plotly_chart(fig, config=config, use_container_width=True)


# Last 10 years trend of Theft and Loss cases in a region
def generate_region_report_10y_linechart(region):
    current_yr = int(modification_date('assets/models/region-total.parquet.gzip'))
    
    df = region_year_total[
        (region_year_total['date'] >= str(current_yr - 10))
        & (region_year_total['region'] == str(region))
    ]

    theft_tr = df.loc[:, ['region', 'date', 'theft']]
    loss_tr = df.loc[:, ['region', 'date', 'loss']]
    
    theft = df['theft'].sum()
    loss = df['loss'].sum()

    htext = "%{y:,.0f}"

    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=theft_tr['date'].dt.year,
            y=theft_tr['theft'],
            name='Theft',
            line={
                'color':clr_theft,
                'width':4
                },
            marker={
                'size':7
                },
            mode='lines+markers',
            hovertemplate=htext,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=loss_tr['date'].dt.year,
            y=loss_tr['loss'],
            name='Loss',
            line={
                'color':clr_loss,
                'width':4
                },
            marker={
                'size':7
                },
            mode='lines+markers',
            hovertemplate=htext,
        )
    )
    
    fig.add_annotation(
        xref='paper',
        yref='paper',
        x=1,
        y=0.5,
        xanchor='left',
        showarrow=False,
        align='left',
        text=f"<span style='font-size=10; color:{clr_secondary_font}'>Total:</span><br><span style='font-size=8; color:{clr_loss}'>&#x2022; Lost: {loss:,}</span><br><span style='font-size=8; color:{clr_theft}'>&#x2022; Stolen: {theft:,}</span>",
        font_family=font_main,
        font_size=12,
        font_color=clr_secondary_font
    )

    # Settings
    fig.update_layout(
        height=160,
        width=400,
        plot_bgcolor=clr_tile_background,
        paper_bgcolor=clr_transparent,
        font_size=14,
        font_color=clr_font,
        margin={
            'l':5,
            'r':110,
            't':30,
            'b':5
            },
        showlegend=False,
        xaxis={
            'title':None,
            'showticklabels':True,
            'gridcolor':clr_page_background,
            # tickmode="array",
            # tickvals=list(theft_tr["date"].dt.year)[::3],
            'dtick':2,
            'tickformat':"%Y",
            'tickfont_size':12,
            'tickfont_family':font_main,
            'tickfont_color':clr_secondary_font,
        },
        yaxis={
            'title':None,
            'showticklabels':True,
            'gridcolor':clr_page_background,
            'zeroline':False,
            'tickfont_size':12,
            'tickfont_family':font_main,
            'tickfont_color':clr_secondary_font,
        },
        hovermode='x unified',
        hoverlabel={
            'bgcolor':'rgba(72,72,72,0.8)',
            'font_color':clr_font
            },
    )
    
    fig.update_layout(
        title=(
            f"""
            <span style='font-size:14px; font-family:{font_main}; color:{clr_secondary_font}'>
            10-year trend
            </span>
            """
            )
        )

    # Watermark
    fig.add_layout_image(
        {
            'source':watermark,
            'x':0.15,
            'y':0.875,
            'sizex':0.7,
            'sizey':0.7,
            'sizing':'contain',
            'opacity':0.05,
            'layer':'above',
        }
    )

    # Disable chart "zoom in" and "zoom out"
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True

    # Hide options bar above the chart
    config = {'displayModeBar': False}

    return st.plotly_chart(fig, config=config, use_container_width=True)
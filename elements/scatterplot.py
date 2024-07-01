import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from utils import modification_date 

# Colors
clr_main = '#2dcdd2'
clr_font = '#dedede'
clr_secondary_font = '#8d9294'

clr_page_background = '#333333'
clr_tile_background = '#292929'
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

def generate_reports_scatterplot(granularity):
    """Generates st.plotly_chart() scatterplot with total numbers of theft and loss records 
    throughout the 1991-[current year] period using the specified time granularity.
    
    Args:
        granularity (str): Scatter plot can represent:
            - 'daily' >>> "Daily Loss and Theft Totals (1991-[current year])"
            - 'weekly' >>> "Weekly Loss and Theft Totals (1991-[current year])"
            - 'monthly' >>> "Monthly Loss and Theft Totals (1991-[current year])" 
            - 'yearly' >>> "Yearly Loss and Theft Totals (1991-[current year])"  

    Returns:
        st.plotly_chart(): Scatter plot
        
    """
    # Data
    date_report_total = pd.read_parquet('assets/models/date-report-total.parquet.gzip')
    
    grouped_day = (
        date_report_total
        .groupby([pd.Grouper(key='date',freq='D'),'report'])['total']
        .sum()
        .reset_index()
        .replace(0, np.nan)
        )
    grouped_week = (
        date_report_total
        .groupby([pd.Grouper(key='date',freq='W'),'report'])['total']
        .sum()
        .reset_index()
        .replace(0, np.nan)
        )
    grouped_month = (
        date_report_total
        .groupby([pd.Grouper(key='date',freq='M'),'report'])['total']
        .sum()
        .reset_index()
        .replace(0, np.nan)
        )
    grouped_year = (
        date_report_total
        .groupby([pd.Grouper(key='date',freq='Y'),'report'])['total']
        .sum()
        .reset_index()
        .replace(0, np.nan)
        )
    
    # Current year 
    current_yr = int(modification_date('assets/models/date-report-total.parquet.gzip','year'))

    # Outlier condition (also used in annotation text, therefore not 0.0 but 0.00 format)
    threshold = 0.90
    
    # Daily outliers
    grouped_day['outlier'] = np.where(
        grouped_day['total'] > grouped_day['total'].quantile(threshold), 
        True, 
        False
        )
    
    # Weekly outliers
    grouped_week['outlier'] = np.where(
        grouped_week['total'] > grouped_week['total'].quantile(threshold), 
        True, 
        False
        )
    
    # Monthly outliers
    grouped_month['outlier'] = np.where(
        grouped_month['total'] > grouped_month['total'].quantile(threshold), 
        True, 
        False
        )
    
    # Yearly outliers
    grouped_year['outlier'] = np.where(
        grouped_year['total'] > grouped_year['total'].quantile(threshold),
        True,
        False
        )
    
    # Hoverlabels
    loss_text = 'Loss: %{y:,.0f}' + '<br>Month: %{x|%B, %d}' + '<br>Year: %{x|%Y}' + '<extra></extra>'
    theft_text = 'Theft: %{y:,.0f}' + '<br>Month: %{x|%B, %d}' + '<br>Year: %{x|%Y}' + '<extra></extra>'
    outlier_text = 'Outlier: %{y:,.0f}' + '<br>Month: %{x|%B, %d}' + '<br>Year: %{x|%Y}' + '<extra></extra>'
    
    # Scatter plot
    fig = go.Figure()
    
    # Daily
    if granularity == 'daily':
        
        # Outliers
        fig.add_trace(
            go.Scattergl(
                x=grouped_day[(grouped_day['outlier'] == True)]['date'],
                y=grouped_day[(grouped_day['outlier'] == True)]['total'],
                mode='markers',
                name=f'Outliers <span style="color:{clr_secondary_font}">(Top {100-int(threshold*100)}%)</span>',
                marker={
                    'size':7,
                    'color':clr_transparent,
                    'line':{
                        'width':4,
                        'color':clr_outlier
                        }
                    },
                hovertemplate=outlier_text,
                hoverlabel={ 
                    'bordercolor':clr_outlier,
                    'font_color':clr_button_text,
                    'bgcolor':clr_outlier
                    }
                )
            )
        
        fig.add_trace(
            go.Scattergl(
                x=grouped_day[(grouped_day['report'] == 'Loss')]['date'],
                y=grouped_day[(grouped_day['report'] == 'Loss')]['total'],
                mode='markers',
                marker={
                    'size':7,
                    'color':clr_loss,
                    'line':{
                        'width':0.19,
                        'color':clr_tile_background
                        }  
                    },
                name='Loss',
                hovertemplate=loss_text,
                hoverlabel={
                    'bordercolor':clr_loss,
                    'font_color':clr_button_text,
                    'bgcolor':clr_loss
                    }
                )
            )
        
        fig.add_trace(
            go.Scattergl(
                x=grouped_day[(grouped_day['report'] == 'Theft')]['date'],
                y=grouped_day[(grouped_day['report'] == 'Theft')]['total'],
                mode='markers',
                marker={
                    'size':7,
                    'color':clr_theft,
                    'line':{
                        'width':0.19,
                        'color':clr_tile_background
                        }  
                    },
                name='Theft',
                hovertemplate=theft_text,
                hoverlabel={ 
                    'bordercolor':clr_theft,
                    'font_color':clr_button_text,
                    'bgcolor':clr_theft
                    }
                )
            )

        fig.update_layout(
            title=f'<b>Daily Lost and Stolen Weapons in Ukraine <span style="color:{clr_secondary_font}">1991-{current_yr}</b></span>',
            )

    # Weekly
    if granularity == 'weekly':
        
         # Outliers
        fig.add_trace(
            go.Scattergl(
                x=grouped_week[(grouped_week['outlier'] == True)]['date'],
                y=grouped_week[(grouped_week['outlier'] == True)]['total'],
                mode='markers',
                name=f'Outliers <span style="color:{clr_secondary_font}">(Top {100-int(threshold*100)}%)</span>',
                marker={
                    'size':9,
                    'color':clr_transparent,
                    'line':{
                        'width':4,
                        'color':clr_outlier
                        }
                    },
                hovertemplate=outlier_text,
                hoverlabel={ 
                    'bordercolor':clr_outlier,
                    'font_color':clr_button_text,
                    'bgcolor':clr_outlier
                    }
                )
            )
        
        fig.add_trace(
            go.Scattergl(
                x=grouped_week[(grouped_week['report'] == 'Loss')]['date'],
                y=grouped_week[(grouped_week['report'] == 'Loss')]['total'],
                mode='markers',
                marker={
                    'size':9,
                    'color':clr_loss,
                    'line':{
                        'width':0.2,
                        'color':clr_tile_background
                        }  
                    },
                name='Loss',
                hovertemplate=loss_text,
                hoverlabel={
                    'bordercolor':clr_loss,
                    'font_color':clr_button_text,
                    'bgcolor':clr_loss
                    }
                )
            )
        
        fig.add_trace(
            go.Scattergl(
                x=grouped_week[(grouped_week['report'] == 'Theft')]['date'],
                y=grouped_week[(grouped_week['report'] == 'Theft')]['total'],
                mode='markers',
                marker={
                    'size':9,
                    'color':clr_theft,
                    'line':{
                        'width':0.2,
                        'color':clr_tile_background
                        }  
                    },
                name='Theft',
                hovertemplate=theft_text,
                hoverlabel={ 
                    'bordercolor':clr_theft,
                    'font_color':clr_button_text,
                    'bgcolor':clr_theft
                    }
                )
            )

        fig.update_layout(
            title=f'<b>Weekly Lost and Stolen Weapons in Ukraine <span style="color:{clr_secondary_font}">1991-{current_yr}</b></span>',
            )

    # Monthly
    if granularity == 'monthly':
        
        # Outliers
        fig.add_trace(
            go.Scattergl(
                x=grouped_month[(grouped_month['outlier'] == True)]['date'],
                y=grouped_month[(grouped_month['outlier'] == True)]['total'],
                mode='markers',
                name=f'Outliers <span style="color:{clr_secondary_font}">(Top {100-int(threshold*100)}%)</span>',
                marker={
                    'size':12,
                    'color':clr_transparent,
                    'line':{
                        'width':5,
                        'color':clr_outlier
                        }
                    },
                hovertemplate=outlier_text,
                hoverlabel={ 
                    'bordercolor':clr_outlier,
                    'font_color':clr_button_text,
                    'bgcolor':clr_outlier
                    }
                )
            )
        
        fig.add_trace(
            go.Scattergl(
                x=grouped_month[(grouped_month['report'] == 'Loss')]['date'],
                y=grouped_month[(grouped_month['report'] == 'Loss')]['total'],
                mode='markers',
                marker={
                    'size':12,
                    'color':clr_loss,
                    'line':{
                        'width':1,
                        'color':clr_tile_background
                        }  
                    },
                name='Loss',
                hovertemplate=loss_text,
                hoverlabel={
                    'bordercolor':clr_loss,
                    'font_color':clr_button_text,
                    'bgcolor':clr_loss
                }
            )
        )
        
        fig.add_trace(
            go.Scattergl(
                x=grouped_month[(grouped_month['report'] == 'Theft')]['date'],
                y=grouped_month[(grouped_month['report'] == 'Theft')]['total'],
                mode='markers',
                marker={
                    'size':12,
                    'color':clr_theft,
                    'line':{
                        'width':1,
                        'color':clr_tile_background
                        }  
                    },
                name='Theft',
                hovertemplate=theft_text,
                hoverlabel={
                    'bordercolor':clr_theft,
                    'font_color':clr_button_text,
                    'bgcolor':clr_theft
                    }
                )
            )
        
        fig.update_layout(
            title=f'<b>Monthly Lost and Stolen Weapons in Ukraine <span style="color:{clr_secondary_font}">1991-{current_yr}</b></span>',
            )
        
    # Yearly
    if granularity == 'yearly':
        
        # Outliers
        fig.add_trace(
            go.Scattergl(
                x=grouped_year[(grouped_year['outlier'] == True)]['date'],
                y=grouped_year[(grouped_year['outlier'] == True)]['total'],
                mode='markers',
                name=f'Outliers <span style="color:{clr_secondary_font}">(Top {100-int(threshold*100)}%)</span>',
                marker={
                    'size':18,
                    'color':clr_tile_background,
                    'line':{
                        'width':8,
                        'color':clr_outlier
                        }
                    },
                hovertemplate=outlier_text,
                hoverlabel={ 
                    'bordercolor':clr_outlier,
                    'font_color':clr_button_text,
                    'bgcolor':clr_outlier
                    }
                )
            )
        
        fig.add_trace(
            go.Scattergl(
                x=grouped_year[(grouped_year['report'] == 'Loss')]['date'],
                y=grouped_year[(grouped_year['report'] == 'Loss')]['total'],
                mode='lines+markers',
                marker={
                    'size':18,
                    'color':clr_loss,
                    'line':{
                        'width':3,
                        'color':clr_tile_background
                        }
                    },
                line={
                    'width':4,
                    },
                name='Loss',
                hovertemplate=loss_text,
                hoverlabel={ 
                    'bordercolor':clr_loss,
                    'font_color':clr_button_text,
                    'bgcolor':clr_loss
                    }
                )
            )
        
        fig.add_trace(
            go.Scattergl(
                x=grouped_year[(grouped_year['report'] == 'Theft')]['date'],
                y=grouped_year[(grouped_year['report'] == 'Theft')]['total'],
                mode='lines+markers',
                marker={
                    'size':18,
                    'color':clr_theft,
                    'line':{
                        'width':3,
                        'color':clr_tile_background
                        }
                    },
                line={
                    'width':4,
                    },
                name='Theft',
                hovertemplate=theft_text,
                hoverlabel={
                    'bordercolor':clr_theft,
                    'font_color':clr_button_text,
                    'bgcolor':clr_theft
                    }
                )
            )

        fig.update_layout(
            title=f'<b>Yearly Lost and Stolen Weapons in Ukraine <span style="color:{clr_secondary_font}">1991-{current_yr}</b></span>',
            )
        
    # Settings
    fig.update_layout(
        height=350,
        width=900,
        plot_bgcolor=clr_tile_background,
        paper_bgcolor=clr_transparent,
        font_color=clr_font,
        font_size=14,
        margin={
            'l':10,
            'r':10, 
            't':70,
            'b':5
            },
        title={
            'font':{
                'size':22, 
                'family':font_main,
                'color':clr_font  
            },
            'x':0.01,
            'xanchor':'left',
            'y':0.95,
            'yanchor':'top'
        },
        showlegend=True,
        legend={
            'orientation':'v',
            'font':{
                'family':font_main,
                'size':14,
                'color':clr_font
            },
            'bgcolor':clr_tile_background,
            'y':0.8,
            'x':1.01,
            'itemsizing':'constant'
        },
        xaxis={
            'title':None,
            'showticklabels':True,
            'tickfont_size':12,
            'tickfont_family':font_main,
            'showspikes':True,
            'spikethickness':1,
            'spikecolor':clr_main,
            'gridcolor':clr_page_background,
            'zeroline':False
            },
        yaxis={
            'title':{
                'text':'Number of Records',
                'font_size':14,
                'font_family':font_main,
                'standoff':5
                },
            'showticklabels':True,
            'tickfont_size':12, 
            'tickfont_family':font_main,
            'showspikes':False,
            'gridcolor':clr_page_background,
            'zeroline':False
            },
        hoverlabel={
            'font_size':13, 
            'font_family':font_main,
        },
        modebar={
            'orientation':'h',
            'bgcolor':clr_transparent,
            'color':clr_main
            },
        updatemenus = [
            {
                'type':'buttons',
                'x':1.02,
                'xanchor':'left',
                'y':0.45,
                'direction':'down',
                'showactive':True,
                'bgcolor':clr_button_background,
                'active':0,
                'bordercolor':clr_button_background,
                'font':{
                    'size':13, 
                    'color':clr_button_text, 
                    'family':font_main
                    },
                'buttons':[
                    {
                        'args':[{
                            'yaxis.type': 'linear',
                            'yaxis.showexponent': 'all',
                            'yaxis.exponentformat': 'B',
                            }],
                        'label':'Linear Scale',
                        'method':'relayout'
                        },
                    {
                        'args':[{
                            'yaxis.type': 'log',
                            'yaxis.showexponent': 'all',
                            'yaxis.exponentformat': 'B',
                            }],
                        'label':'Log Scale',
                        'method':'relayout'
                        },
                    ],
                },
            ]
        )

    # Add watermark
    fig.add_layout_image(
        {
            'source':watermark,
            'x':0.075,
            'y':0.95,
            'sizex':0.9,
            'sizey':0.9,
            'sizing':'contain',
            'opacity':0.04,
        }
    )

    # Hide unnecessary buttons from plot
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

    return st.plotly_chart(fig, config=config, use_container_width=True)


# Scatter table
def generate_weapons_scatterplot():
    
    # Data
    model_region_weaponcategory_total = pd.read_parquet("assets/models/region-weaponcategory-total.parquet.gzip")

    # Function to insert line breaks
    def insert_line_breaks(weaponcategory_name):

        if ' ' in weaponcategory_name:
            return weaponcategory_name.replace(' ', '<br>')

        elif '&' in weaponcategory_name:
            return weaponcategory_name.replace('&', '<br>and<br>')

        else:
            return weaponcategory_name

    # Apply the function to the 'weaponcategory' column
    model_region_weaponcategory_total['weaponcategory'] = model_region_weaponcategory_total['weaponcategory'].apply(insert_line_breaks)
    
    # Scale up values for better markers diplay
    model_region_weaponcategory_total['total_log100'] = (model_region_weaponcategory_total['total_log100'] + 0.1) 

    # Colors
    favcol = ["#00383b","#0B787C","#16B8BE","#21f8ff","#faffff"]


    fig = px.scatter(
        model_region_weaponcategory_total,
        x="weaponcategory",
        y="region",
        color="total",
        size="total_log100",
        opacity=1,
        color_continuous_scale=[
            # Colorbar ranges
            [0, favcol[0]],
            [0.001, favcol[0]],  # 0%-0.1% (smallest values & colorbar bottom)
            [0.001, favcol[1]],
            [0.01, favcol[1]],  # 0.1%-1%
            [0.01, favcol[2]],
            [0.05, favcol[2]],  # 1%-5%
            [0.05, favcol[3]],
            [0.2, favcol[3]],  # 5%-20%
            [0.2, favcol[4]],
            [1, favcol[4]],  # 20%-100% (largest values & colorbar top)
        ],
        hover_data={
            "region": False,
            f"<span style='color:{clr_secondary_font}'>Region</span>": model_region_weaponcategory_total["region"],
            "weaponcategory": False,
            f"<span style='color:{clr_secondary_font}'>Weapon category</span>": model_region_weaponcategory_total["weaponcategory"],
            "total": False,
            f"<span style='color:{clr_secondary_font}'>Number of records</span>": (":,", model_region_weaponcategory_total["total"]),
            "local_rank": False,
            f"<span style='color:{clr_secondary_font}'>Local rank</span>": model_region_weaponcategory_total["local_rank"],
            "country_rank": False,
            f"<span style='color:{clr_secondary_font}'>Country rank</span>": model_region_weaponcategory_total["country_rank"],
            "total_log100": False,
            # custom data
            f"<span style='color:{clr_secondary_font}'>% of Region Total</span>": (
                ":.3%",
                model_region_weaponcategory_total["total"] / model_region_weaponcategory_total["total_region"],
            ),
            f"<span style='color:{clr_secondary_font}'>% of Country Total</span>": (
                ":.4%",
                model_region_weaponcategory_total["total"] / model_region_weaponcategory_total["total_country"],
            ),
        },
    )

    fig.update_layout(
        width=1400,
        height=1000,
        plot_bgcolor=clr_tile_background,
        paper_bgcolor=clr_transparent,
        margin={
            'l':150, 
            'r':10,
            't':30,
            'b':0
            },
        xaxis={
            'title':None,
            'tickfont_color':clr_font,
            'gridcolor':clr_page_background,
            'tickfont_size':13,
            'tickfont_family':font_main,
            'side':'top',
            'ticks':'outside',
            'anchor':'free', 
            'position':0.96
            },
        yaxis={
            'title':None,
            'gridcolor':clr_page_background,
            'tickfont_color':clr_font,
            'tickfont_size':14,
            'tickfont_family':font_main,
            'ticks':'outside',
            },
        coloraxis_colorbar={
            'y':0.5,
            'title':None,
            'titlefont_color':clr_font,
            'tickfont_color':clr_font,
            'tickfont_size':13,
            'tickfont_family':font_main,
            'ticks':'outside',
            },
        hoverlabel={
            'bgcolor':clr_hoverlabel,
            'bordercolor':clr_hoverlabel, 
            'font_color':clr_font,
            'font_family':font_main,
            'font_size':13,
            },
        modebar={
            'orientation':'h',
            'bgcolor':clr_transparent,
            'color':clr_main
            },
        )

    fig.update_traces(
        marker={
            'line':{
                'width':0,
                'color':clr_tile_background,
                }
            }
        )

    # Disable chart "zoom in" and "zoom out"
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True

    # Hide options bar above the chart
    config = {"displayModeBar": False}

    return st.plotly_chart(fig, config=config, use_container_width=True)

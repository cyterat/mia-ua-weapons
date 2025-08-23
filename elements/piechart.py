import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def generate_reports_piechart(year=2023):
    
    tl_count = pd.read_parquet("data/marts/date-report-total.parquet").astype({"report":"str"}).groupby([pd.Grouper(key='date', freq='Y'), 'report'])['total'].sum().reset_index()
    tl_count = tl_count[tl_count['date'].dt.year==int(year)]
    
    clr_loss = '#679496'
    clr_theft = '#006C72'
    clr_font = '#dedede'
    clr_tile_background = '#292929'
    clr_transparent = 'rgba(0,0,0,0)'
    
    font_main = 'Montserrat, sans-serif'
    
    fig = go.Figure()
    
    fig.add_pie(
        labels=tl_count["report"],
        values=tl_count["total"],
        hole=.5,
        marker={
            'colors':[clr_loss, clr_theft], 
            'line':{
                'color':clr_tile_background,
                'width':5
                }
            },
        showlegend=False,
        textinfo='label+percent',
        hoverinfo='skip',
        )
    
    fig.add_annotation(
        text=f"<b>{sum(tl_count['total']):,.0f}<br>records</b>", 
        x=0.5, 
        y=0.5, 
        font_size=20,
        font_family=font_main,
        font_color=clr_font, 
        showarrow=False
    )
    
    fig.update_layout(
        height=300,
        plot_bgcolor=clr_tile_background,
        paper_bgcolor=clr_transparent,
        font_size=12,
        font_family=font_main,
        font_color=clr_font,
        margin={
            'l':10, 
            'r':10, 
            't':10, 
            'b':10
            }
        )
    
    # Hide options bar above the chart
    config = {"displayModeBar": False}
    
    return st.plotly_chart(fig, config=config, use_container_width=True)
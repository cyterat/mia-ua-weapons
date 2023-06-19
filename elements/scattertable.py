import streamlit as st
import pandas as pd
import plotly.express as px

# Colors
favcol = ["#00383b", "#004a4f", "#009ba1", "#21f8ff", "#faffff"]


# Scatter table
def scatter_table():
    # Data
    cat_ua_df = pd.read_parquet("assets/models/cat-ua-df.parquet.gzip")

    fig = px.scatter(
        cat_ua_df,
        x="weaponcategory",
        y="region",
        color="frequency",
        size="freqLog100",
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
            "Region": cat_ua_df["region"],
            "weaponcategory": False,
            "Weapon category": cat_ua_df["weaponcategory"],
            "frequency": False,
            "Number of records": (":,", cat_ua_df["frequency"]),
            "local_rank": False,
            "Local rank": cat_ua_df["local_rank"],
            "country_rank": False,
            "Country rank": cat_ua_df["country_rank"],
            "freqLog100": False,
            # custom data
            "% of Region Total": (
                ":.3%",
                cat_ua_df["frequency"] / cat_ua_df["total_region"],
            ),
            "% of Country Total": (
                ":.4%",
                cat_ua_df["frequency"] / cat_ua_df["total_country"],
            ),
        },
    )

    fig.update_layout(
        width=1400,
        height=1000,
        plot_bgcolor="#414141",  # rgba(0,0,0,0)
        paper_bgcolor="#414141",
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(
            title=None,
            tickfont_color="#F0F0F0",
            gridcolor="#414141",
            tickfont_size=13,
            tickfont_family="Verdana, sans-serif",
            side="top",
            ticks="outside",
        ),
        yaxis=dict(
            title=None,
            gridcolor="#484848",  # 484848 #414141
            tickfont_color="#F0F0F0",
            tickfont_size=14,
            tickfont_family="Verdana, sans-serif",
            ticks="outside",
        ),
        coloraxis_colorbar=dict(
            y=0.5,
            title="",
            titlefont_color="#F0F0F0",
            tickfont_color="#F0F0F0",
            tickfont_size=13,
            tickfont_family="Verdana",
            ticks="outside",
        ),
        hoverlabel=dict(
            bgcolor="rgba(72,72,72,0.8)",  # 484848
            bordercolor="rgba(72,72,72,0.8)",  # 484848
            font_color="#F0F0F0",
            font_family="Verdana, sans-serif",
            font_size=13,
        ),
    )

    fig.update_xaxes(anchor="free", position=0.98)

    fig.update_traces(marker=dict(line=dict(width=0.6)))

    # Disable chart "zoom in" and "zoom out"
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True

    # Hide options bar above the chart
    config = {"displayModeBar": False}

    return st.plotly_chart(fig, config=config, use_container_width=True)

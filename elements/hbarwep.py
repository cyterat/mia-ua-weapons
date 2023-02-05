import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.offsetbox import (OffsetImage, AnchoredOffsetbox)
from matplotlib.ticker import StrMethodFormatter

def hbar_wep():
    weapons_df = pd.read_parquet('assets/models/agg-weapon-ctgr.parquet.gzip')

    matplotlib_wtrmrk='assets/cyan-tesseract-3d-200x200.png'

    #Horizontal bar chart
    fig, ax = plt.subplots(figsize=(2,3))
    ax.barh(weapons_df.sort_index(ascending=False).index, width=weapons_df.sort_index(ascending=False)['total'], color="#00CCD3",)
        
    ax.spines.top.set(visible=False)
    ax.spines.bottom.set(visible=True, color='#484848')
    ax.spines.right.set(visible=False)
    ax.spines.left.set(visible=True, color='#484848')
        
    plt.xticks(color='#eeeeee', size=7)
    plt.yticks(color='#eeeeee', size=9)

    plt.locator_params(axis='x', nbins=4)
    ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

    ax.set_facecolor('#333333')
    fig.set_facecolor('#333333')
    plt.grid(axis='x', color='#484848')

    plt.title(
        'Total Number of Records\nin each Weapon Category', 
        pad=15, 
        fontdict=dict(
            fontsize=11, 
            fontweight='bold', 
            color='#dedede'
        )
    )

    #Watermark
    def watermark2(ax):
        img = Image.open(matplotlib_wtrmrk)
        width, height = ax.figure.get_size_inches()*fig.dpi
        wm_width = int(width/4.5) # make the watermark 1/4 of the figure size
        scaling = (wm_width / float(img.size[0]))
        wm_height = int(float(img.size[1])*float(scaling))
        img = img.resize((wm_width, wm_height))

        imagebox = OffsetImage(img, zoom=1, alpha=0.05)
        imagebox.image.axes = ax

        ao = AnchoredOffsetbox('center', pad=0.01, borderpad=0, child=imagebox)
        ao.patch.set_alpha(0)
        ax.add_artist(ao)

    watermark2(ax)

    #Totals for each bar
    for i in ax.patches:
        plt.text(
            i.get_width()+2000, 
            i.get_y()+0.26,
            f"{round((i.get_width()), 2):,}",
            fontsize=8,
            color='#dedede'
        )
        
    ax.set_axisbelow(True)

    #Closing matplotlib 
    plt.close()
    return st.pyplot(fig)
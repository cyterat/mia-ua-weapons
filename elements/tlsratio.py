import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.offsetbox import (OffsetImage, AnchoredOffsetbox)

def tls_ratio():
        
    bicolor = ['#00595e','#faffff']

    tl_count = pd.read_parquet('assets/models/tls-ratio.parquet.gzip')

    matplotlib_wtrmrk='assets/cyan-tesseract-3d-200x200.png'

    fig, ax = plt.subplots(figsize=(6,6))

    patches, texts, pcts = plt.pie(
        x=tl_count['frequency'],
        labels=tl_count['report'],
        colors=bicolor,
        radius=1,
        autopct='%.0f%%',
        startangle = 90,
        pctdistance=0.75,
        wedgeprops=dict(
            width=0.5,
            edgecolor='#333333',
            lw=6
        ),
        #Segment labels font
        textprops=dict(
            weight='bold',
            size=16
        )
    )

    #Formatting circle center values 
    plt.text(0, -0.05, f"{int(sum(tl_count['frequency'])/1000)}k\nrecords", ha='center', va='center', fontsize=24, color='#DEDEDE')

    #Formating segment values' font
    for i, num in enumerate(pcts):
        pcts[i].set_color(bicolor[::-1][i])

                        
    plt.setp(pcts, fontweight='bold', fontsize=14)

    #Colored labels based on the respective segment
    for i, patch in enumerate(patches):
        texts[i].set_color(patch.get_facecolor())

    plt.title('Ukraine', y=-0.01, fontsize=16, color='#DEDEDE')

    fig.set_facecolor('#333333')

    def watermark2(ax):
        img = Image.open(matplotlib_wtrmrk)
        width, height = ax.figure.get_size_inches()*fig.dpi
        wm_width = int(width/5) # make the watermark 1/4 of the figure size
        scaling = (wm_width / float(img.size[0]))
        wm_height = int(float(img.size[1])*float(scaling))
        img = img.resize((wm_width, wm_height))

        imagebox = OffsetImage(img, zoom=1, alpha=0.05)
        imagebox.image.axes = ax

        ao = AnchoredOffsetbox('center', pad=0.01, borderpad=0, child=imagebox)
        ao.patch.set_alpha(0)
        ax.add_artist(ao)

    watermark2(ax)

    #Closing matplotlib 
    plt.close()
    return st.pyplot(fig)
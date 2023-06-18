import streamlit as st
import pandas as pd
import numpy as np
import os.path, time
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnchoredOffsetbox


# File modification year
def modification_date(file):
    t = os.path.getmtime(file)
    year, month, day, hour, minute, second = time.localtime(t)[:-3]
    date = f"{year}"
    return date


def top_5():
    colors = ["#007a81", "#faffff"]

    top = pd.read_parquet("assets/models/country-stats.parquet.gzip").nlargest(
        5, "frequency"
    )

    top5 = pd.read_parquet("assets/models/top5.parquet.gzip")

    matplotlib_wtrmrk = "assets/cyan-tesseract-3d-200x200.png"

    fig, ax = plt.subplots(figsize=(3, 4))
    left = np.zeros(len(top5))

    for i, col in enumerate(top5.columns):
        ax.barh(
            top5.index,
            top5[col],
            left=left,
            label=col,
            color=colors[i],
            height=0.4,
        )
        left += np.array(top5[col])

    # Bars' totals
    totals = top5.sum(axis=1)

    for i, total in enumerate(totals):
        ax.text(
            total + 2000,  # distance from bar
            i - 0.08,  # vertical position with respect to a bar
            f"{round(total):,}",
            color="#F0F0F0",
            size=9,
        )

    ax.set_facecolor("#414141")
    ax.legend(
        labels=["Lost", "Stolen"],
        ncol=2,
        mode="expand",
        fontsize="medium",
        facecolor="#414141",
        edgecolor="#414141",
        labelcolor="#F0F0F0",
        loc=(0.1, -0.1),
        prop={"size": 9},
    )

    ax.spines.top.set(visible=False)
    ax.spines.bottom.set(visible=False)
    ax.spines.right.set(visible=False)
    ax.spines.left.set(visible=True, color="#484848")

    fig.set_facecolor("#414141")

    plt.xticks([])
    plt.yticks(color="#F0F0F0", size=10)

    plt.title(
        "Top 5 Regions of Ukraine\nwith the Largest Number\nof Weapons Theft and Loss Cases",
        pad=15,
        fontdict=dict(
            fontsize=12,
            # fontweight='bold',
            color="#F0F0F0",
        ),
    )

    # Anntations
    plt.annotate(
        f'The top 5 out of 25\nregions of Ukraine\nmake up {int(top["pct_of_total"].sum()*100)}% of all\nrecords in the\ncountry.',
        xy=(3.3, 1),
        xytext=(totals.max() - totals.max() * 0.05, 1.1),
        fontsize=9,
        color="#F0F0F0",
    )

    current_yr = int(modification_date("assets/models/country-stats.parquet.gzip"))

    plt.annotate(
        f"Chart: cyterat ⋅ Source: MIA of Ukraine ⋅ {current_yr}",
        xy=(3.3, 1),
        xytext=(totals.max() * -0.45, -1.25),
        fontsize=8,
        color="#F0F0F0",
    )

    def watermark2(ax):
        img = Image.open(matplotlib_wtrmrk)
        width, height = ax.figure.get_size_inches() * fig.dpi
        wm_width = int(width / 2)  # make the watermark 1/2 of the figure size
        scaling = wm_width / float(img.size[0])
        wm_height = int(float(img.size[1]) * float(scaling))
        img = img.resize((wm_width, wm_height))

        imagebox = OffsetImage(img, zoom=1, alpha=0.05)
        imagebox.image.axes = ax

        ao = AnchoredOffsetbox("center", pad=0.01, borderpad=0, child=imagebox)
        ao.patch.set_alpha(0)
        ax.add_artist(ao)

    watermark2(ax)

    # Closing matplotlib
    plt.close()

    return st.pyplot(fig)

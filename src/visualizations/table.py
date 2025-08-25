import streamlit as st
from matplotlib.colors import ListedColormap

# Colors
clr_main ="#26c8cd"
clr_outlier = "#e54848"
clr_tile_background = "#292929"
clr_page_background ="#333333"
clr_font = "#dedede"
clr_secondary_font = "#8d9294"
clr_transparent = "rgba(0,0,0,0)"

# Font
font_family = 'Montserrat, sans-serif'


def generate_region_total_table(
    df,
    cmap_colors=[clr_secondary_font, '#8a3d3f', clr_outlier],
):
    """
    Apply a custom style to a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame to apply the background gradient to.
        cmap_colors (List[str]): List of color values for the colormap.
        low (int or float): Lowest value in the range (default: 0).
        high (int or float): Highest value in the range (default: 0).

    Returns:
        pd.DataFrame: DataFrame with applied styles.
    """
    
    df.index.name = None
    
    # Colormap of the provided colors
    cmap = ListedColormap(cmap_colors)
    
    # Apply the background gradient to the DataFrame
    styled_df = (
        df
        .style
        .format({
            "total": "{:,}",
            "loss": "{:,}",
            "theft": "{:,}",
            "total_pct": "{:.1%}",
            "loss_pct": "{:.0%}",
            "theft_pct": "{:.0%}"
            })
        .text_gradient(
            subset=['total'],
            cmap=cmap,
            vmin=df['total'].quantile(0.5),
            vmax=df['total'].quantile(0.9)
            )
        .text_gradient(
            subset=['loss'],
            cmap=cmap,
            vmin=df['loss'].quantile(0.5),
            vmax=df['loss'].quantile(0.9)
            )
        .text_gradient(
            subset=['theft'],
            cmap=cmap,
            vmin=df['theft'].quantile(0.5),
            vmax=df['theft'].quantile(0.9)
            )
        .text_gradient(
            subset=['total_pct'],
            cmap=cmap,
            vmin=0.05,
            vmax=0.1
            )
        .text_gradient(
            subset=['loss_pct'],
            cmap=cmap,
            vmin=df['loss_pct'].quantile(0.5),
            vmax=df['loss_pct'].quantile(1.0)
            )
        .text_gradient(
            subset=['theft_pct'],
            cmap=cmap,
            vmin=df['theft_pct'].quantile(0.5),
            vmax=df['theft_pct'].quantile(1.0)
            )
        )
    
    return st.table(styled_df)


def generate_weaponcategory_total_table(
    df,
    cmap_colors=[clr_secondary_font, '#8a3d3f', clr_outlier],
):
    """
    Apply a custom style to a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame to apply the background gradient to.
        cmap_colors (List[str]): List of color values for the colormap.
        low (int or float): Lowest value in the range (default: 0).
        high (int or float): Highest value in the range (default: 0).

    Returns:
        pd.DataFrame: DataFrame with applied styles.
    """
    
    df.index.name = None
    
    # Colormap of the provided colors
    cmap = ListedColormap(cmap_colors)
    
    # Apply the background gradient to the DataFrame
    styled_df = (
        df
        .style
        .format({
            "total": "{:,}",
            "loss": "{:,}",
            "theft": "{:,}",
            })
        .text_gradient(
            subset=['total'],
            cmap=cmap,
            vmin=df['total'].quantile(0.5),
            vmax=df['total'].quantile(0.9)
            )
        .text_gradient(
            subset=['loss'],
            cmap=cmap,
            vmin=df['loss'].quantile(0.5),
            vmax=df['loss'].quantile(0.9)
            )
        .text_gradient(
            subset=['theft'],
            cmap=cmap,
            vmin=df['theft'].quantile(0.5),
            vmax=df['theft'].quantile(0.9)
            )
        )
    
    return st.table(styled_df)



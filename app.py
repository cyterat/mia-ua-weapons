import streamlit as st
import pandas as pd
import numpy as np

from elements import generate_events_barchart
from elements import generate_reports_scatterplot
from elements import generate_reports_piechart
from elements import generate_weapons_scatterplot
from elements import generate_region_total_table
from elements import generate_weaponcategory_total_table

from elements import generate_rank_region_population
from elements import generate_region_total_linechart
from elements import generate_region_weapons_polarchart
from elements import generate_region_report_10y_linechart

from utils import modification_date  
from utils import current_total_records  


# ========================#
# --------SETTINGS--------#

# Page
st.set_page_config(
    page_title="Lost and Stolen Weapons in Ukraine",
    layout="wide",
    )

# Style
with open('style.css') as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
        )

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


# ====================#
# --------DATA--------#

region_total = pd.read_parquet("assets/models/region-total.parquet.gzip")
top = region_total.nlargest(5, "total")
bot = region_total.nsmallest(5, "total")

model_weaponcategory_total = pd.read_parquet("assets/models/weaponcategory-total.parquet.gzip").set_index('weaponcategory')
model_region_year_total = pd.read_parquet("assets/models/region-year-total.parquet.gzip")
date_report_total = pd.read_parquet("assets/models/date-report-total.parquet.gzip")
# population = pd.read_csv("assets/ua-population.csv").iloc[:,[0,-2,-1]]

# File modification year
current_date = modification_date("assets/models/region-total.parquet.gzip","date")


# ====================#
# --------PAGE--------#

# Spinner
with st.spinner("Please wait a few seconds while I prepare everything...🔥"):


    # =====================#
    # --------TITLE--------#
    
    st.markdown(
        f"""
        <div class="page-header">
            <div class="main-title">
                LOST AND STOLEN WEAPONS IN UKRAINE
            </div>
            <div class="main-subtitle">
                This webpage is a visual representation of the dataset provided by MIA of Ukraine to the open data portal under the Creative Commons Attribution license.<br> 
                <a style=text-align: center; href="https://github.com/cyterat"><img src="https://images2.imgbox.com/3f/e6/RqycpnL4_o.png" alt="cyterat" width="25" height="30"></a>
                <span style='color: #838383; font-size: 15px'>Last update: {current_date}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
        )
    
    
    # =========================#
    # --------SECTION 1--------#

    # Barchart
    generate_events_barchart()


    # =========================#
    # --------SECTION 2--------#
    
    # Metrics
    overall_total = date_report_total['total'].sum()
    overall_total_l = date_report_total[date_report_total["report"] == "Loss"]['total'].sum()
    overall_total_t = date_report_total[date_report_total["report"] == "Theft"]['total'].sum()
    
    # tmp (~population according to the IDSS of Ukraine)
    current_population =  34000000
    delta_population = 8000000

    current_date, current_total, new_records, delta_color, sign = current_total_records(info="total")
    current_date, current_total_l, new_records_l, delta_color_l, sign_l = current_total_records(info="loss")
    current_date, current_total_t, new_records_t, delta_color_t, sign_t = current_total_records(info="theft")
    
    st.markdown(
        f"""
        <div class=total-metric>
            <button disabled class='total-metric-item'>
                <span title='According to IDSS, the population of Ukraine was between 28 and 34 million as of January 1, 2023.'>
                    <span style='font-size: 15px'>~ Population (2023) <sup>?</sup></span><br>
                    <span style='font-size: 36px'>{current_population:,}</span><br>
                    <span style='color: {delta_color}; font-size: 15px'>-{delta_population:,}</span>
                </span>
            </button>
            <button disabled class='total-metric-item'>
                <span title='Delta represents number of the newly added records (monthly update)'>
                    <span style='font-size: 15px'>Total Records <sup>?</sup></span><br>
                    <span style='font-size: 36px'>{overall_total:,}</span><br>
                    <span style='color: {delta_color}; font-size: 15px'>{sign}{new_records:,}</span>
                </span>
            </button>
            <button disabled class='total-metric-item'>
                <span title='Delta represents number of the newly added records (monthly update)'>
                    <span style='font-size: 15px'>Total Weapons Lost <sup>?</sup></span><br>
                    <span style='font-size: 36px'>{overall_total_l:,}</span><br>
                    <span style='color: {delta_color_l}; font-size: 15px'>{sign_l}{new_records_l:,}</span>
                </span>
            </button>
            <button disabled class='total-metric-item'>
                <span title='Delta represents number of the newly added records (monthly update)'>
                    <span style='font-size: 15px'>Total Weapons Stolen <sup>?</sup></span><br>
                    <span style='font-size: 36px'>{overall_total_t:,}</span><br>
                    <span style='color: {delta_color_t}; font-size: 15px'>{sign_t}{new_records_t:,}</span>
                </span>
            </button>
            <button disabled class='total-metric-item'>
                <span style='font-size: 15px'>Records ({current_date})</span><br>
                <span style='font-size: 36px'>{current_total:,}</span><br>
            </button>
            <button disabled class='total-metric-item'>
                <span style='font-size: 15px'>Weapons Lost ({current_date})</span><br>
                <span style='font-size: 36px'>{current_total_l:,}</span><br>
            </button>
            <button disabled class='total-metric-item'>
                <span style='font-size: 15px'>Weapons Stolen ({current_date})</span><br>
                <span style='font-size: 36px'>{current_total_t:,}</span><br>
            </button>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    
    # =========================#
    # --------SECTION 3--------#
    
    # TLDR (Overview)
    st.markdown(
        f"""
        <div class="section-header">
            TL;DR
        </div>
        """,
        unsafe_allow_html=True
        )
    
    sec3_col1, sec3_col2 = st.columns((1.1, 2))
    
    with sec3_col1:
        
        generate_region_total_table(region_total.set_index('region'))
        
    with sec3_col2:
        
        total_prev = (
            model_region_year_total[model_region_year_total["date"].dt.year < 2014]
            .groupby(["region"])["total"]
            .sum()
            .reset_index()["total"]
            .sum()
        )
        total_2014 = (
            model_region_year_total[model_region_year_total["date"].dt.year == 2014]
            .groupby(["region"])["total"]
            .sum()
            .reset_index()["total"]
            .sum()
        )
        pct_diff_2014 = int(total_2014 / total_prev * 100)
        diff_2014 = (total_2014 - total_prev)
        
        st.markdown(
            # <div class='total-metric-item' style='font-family:{font_family}'>
            f"""
            <div class='tldr' style='font-family:{font_family}'>
                <ul>
                    In <span style='color: {clr_main}'>2014</span> there were nearly <span title='{diff_2014:,} records' style='color: {clr_main}'>{pct_diff_2014}% more records</span> than in all previous years combined.
                </ul>
                <ul>
                    <span style='color: {clr_main}'>2017</span> had an abnormally high number of <span style='color: {clr_main}'>lost weapons in the Donetsk and Luhansk regions</span>. No particularly significant events 
                    which would explain this anomaly took place during that period, except for the <span style='color: {clr_main}'>large-scale police reform in 2015</span>.
                </ul>
                <ul>
                    <span style='color: {clr_main}'>Simferopol</span> (Crimea) region accounts for around <span title="{int(top[top['region']=='Simferopol']['total']):,} records" style='color: {clr_main}'>{int(round(top[top['region']=='Simferopol']['total_pct'], 2)*100)}%</span> of all records. 
                    The main contributor to this high percentage was the <span style='color: {clr_main}'>2014</span> annexation, meaning that all 
                    <span style='color: {clr_main}'>weapons registered</span> there were likely <span style='color: {clr_main}'>labeled as lost or stolen</span>.
                    The same applies to the <span style='color: {clr_main}'>Donetsk</span> region, which makes up approximately <span title="{int(top[top['region']=='Donetsk']['total']):,} records" style='color: {clr_main}'>{int(round(top[top['region']=='Donetsk']['total_pct'], 2)*100)}%</span> of all records. 
                </ul>
                <ul>
                    The <span style='color: {clr_main}'>tiniest</span> share of the country records has the <span style='color: {clr_main}'>{bot.iloc[0,0]}</span> region, 
                    around <span title="{bot.iloc[0]['total']:,} records" style='color: {clr_main}'>{round(bot.iloc[0]['total_pct'], 3)*100:.1f}%</span>. 
                    It is closely followed by <span style='color: {clr_main}'>{bot.iloc[1,0]}</span>, accounting for 
                    <span title="{bot.iloc[1]['total']:,} records" style='color: {clr_main}'>{round(bot.iloc[1]['total_pct'], 3)*100:.1f}%</span> of all reports.
                </ul>
                <ul>
                    <span style='color: {clr_main}'>{region_total.loc[region_total['theft_pct'].idxmin()]['region']}</span> has the 
                    <span style='color: {clr_main}'>lowest</span> percentage of <span style='color: {clr_main}'>theft</span> reports, 
                    only <span title="{region_total.loc[region_total['theft_pct'].idxmin()]['theft']:,} records" 
                    style='color:{clr_main}'>{int(round(region_total.loc[region_total['theft_pct'].idxmin(),'theft_pct'], 2)*100)}%</span>, and the 
                    <span style='color: {clr_main}'>highest loss</span> percentage, nearly 
                    <span title="{region_total.loc[region_total['loss_pct'].idxmax()]['loss']:,} records" 
                    style='color:{clr_main}'>{int(round(region_total.loc[region_total['loss_pct'].idxmax(),'loss_pct'], 2)*100)}%</span>.
                    By contrast, <span style='color: {clr_main}'>{region_total.loc[region_total['theft_pct'].idxmax()]['region']} </span>
                    has around <span title="{region_total.loc[region_total['theft_pct'].idxmax()]['theft']:,} records" 
                    style='color:{clr_main}'>{int(round(region_total.loc[region_total['theft_pct'].idxmax(),'theft_pct'], 2)*100)}%</span> 
                    of its records being <span style='color: {clr_main}'>theft</span> reports,
                    the <span style='color: {clr_main}'>highest</span> number among all regions.
                </ul>
                <ul>
                    The <span style='color: {clr_main}'>two</span> most "popular" 
                    <span style='color: {clr_main}'>weapon categories</span>, which are making up almost 
                    <span title='{model_weaponcategory_total.loc[model_weaponcategory_total.index[:2],'total'].sum():,} records' 
                    style='color:{clr_main}'>{(model_weaponcategory_total.loc[model_weaponcategory_total.index[:2],'total'].sum()/model_weaponcategory_total.loc[:,'total'].sum())*100:.0f}%</span> of all records, are 
                    <span title='{model_weaponcategory_total.loc[model_weaponcategory_total.index[0],'total'].sum():,} records' 
                    style='color: {clr_main}'>{model_weaponcategory_total.index[0]}</span> and 
                    <span title='{model_weaponcategory_total.loc[model_weaponcategory_total.index[1],'total'].sum():,} records' 
                    style='color: {clr_main}'>{model_weaponcategory_total.index[1]}</span>.
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


    # =========================#
    # --------SECTION 4--------#
    
    # Reports
    st.markdown(
        f"""
        <div class="section-header">
            Reports
        </div>
        """,
        unsafe_allow_html=True
        )
    
    sec4_col1, sec4_col2 = st.columns((5,1))
    
    with sec4_col1: 
        tab1, tab2, tab3, tab4 = st.tabs(['Yearly','Monthly', 'Weekly','Daily'])
        # Scatter plots
        with tab1:
            generate_reports_scatterplot('yearly')
        
        with tab2:
            generate_reports_scatterplot('monthly')
        
        with tab3:
            generate_reports_scatterplot('weekly')
        
        with tab4:
            generate_reports_scatterplot('daily')
    
    with sec4_col2:
        
        year = st.selectbox(label='', options=np.arange(1991, int(modification_date("assets/models/region-total.parquet.gzip",'year'))+1, 1), label_visibility='hidden')
    
        generate_reports_piechart(year)
        
        
    # =========================#
    # --------SECTION 5--------#
    
    # Weapon categories
    st.markdown(
        f"""
        <div class="section-header">
            Weapon Categories
        </div>
        """,
        unsafe_allow_html=True
        )
    
    sec5_col1, sec5_col2 = st.columns((1.1, 3))

    with sec5_col1:
        # Table
        generate_weaponcategory_total_table(model_weaponcategory_total)

        # Weapon categories explanations
        st.markdown(
            f"""
            
            * <span title='{model_weaponcategory_total.loc["Artillery",'total']} records, {model_weaponcategory_total.loc["Artillery",'total'] / model_weaponcategory_total['total'].sum():.2%} of total' style='color: {clr_main}'>Artillery</span><br><small> grenade launcher, mortar, ATGM, MANPAD, etc.</small>
            
            * <span title='{model_weaponcategory_total.loc["Bladed",'total']} records, {model_weaponcategory_total.loc["Bladed",'total'] / model_weaponcategory_total['total'].sum():.2%} of total' style='color: {clr_main}'>Bladed</span><br><small> knife, sword, bayonet, saber, etc.</small>
            
            * <span title='{model_weaponcategory_total.loc["Handguns",'total']} records, {model_weaponcategory_total.loc["Handguns",'total'] / model_weaponcategory_total['total'].sum():.2%} of total' style='color: {clr_main}'>Handguns</span><br><small> pistol, revolver, machine pistol, traumatic pistol, etc.</small>
            
            * <span title='{model_weaponcategory_total.loc["Heavy firearms",'total']} records, {model_weaponcategory_total.loc["Heavy firearms",'total'] / model_weaponcategory_total['total'].sum():.2%} of total' style='color: {clr_main}'>Heavy firearms</span><br><small> autocannon, cannon, machine gun, anti-tank rifle, etc.</small>
            
            * <span title='{model_weaponcategory_total.loc["Light firearms",'total']} records, {model_weaponcategory_total.loc["Light firearms",'total'] / model_weaponcategory_total['total'].sum():.2%} of total' style='color: {clr_main}'>Light firearms</span><br><small> assault rifle, carabine, shotgun, marksman rifle, etc.</small>
            
            * <span title='{model_weaponcategory_total.loc["Other",'total']} records, {model_weaponcategory_total.loc["Other",'total'] / model_weaponcategory_total['total'].sum():.2%} of total' style='color: {clr_main}'>Other</span><br><small> receiver, ammunition, crossbow, carabine replica, etc.</small>
            
            * <span title='{model_weaponcategory_total.loc["Pneumatic&Flobert",'total']} records, {model_weaponcategory_total.loc["Pneumatic&Flobert",'total'] / model_weaponcategory_total['total'].sum():.2%} of total' style='color: {clr_main}'>Pneumatic&Flobert</span><br><small> pneumatic rifle, pneumatic pistol, Flobert rifle, Flobert revolver, etc.</small>
            
            * <span title='{model_weaponcategory_total.loc["Explosives",'total']} records, {model_weaponcategory_total.loc["Explosives",'total'] / model_weaponcategory_total['total'].sum():.2%} of total' style='color: {clr_main}'>Explosives</span><br><small> explosive material, grenade, rocket, shell, etc.</small>
            
            """,
            unsafe_allow_html=True,
        )
        
    with sec5_col2:
        # "Scatterplot"
        generate_weapons_scatterplot()


    # =========================#
    # --------SECTION 6--------#
    
    # Regional records
    st.markdown(
        f"""
        <div class="section-header">
            Regional Records<br>
            <span style='font-size:14px; color:{clr_secondary_font}; display: inline-block;'>
                Administrative centers here represent entire regions (oblasts)<br>
                Ranked by the total number of records, where #1 region has the most records in Ukraine
            </span>
        </div>
        """,
        unsafe_allow_html=True
        )

    with st.container():
        
        # Cherkasy
        a1, a2, a3, a4, _ = st.columns(
            
            # (0.3, 0.1, 0.3, 0.25, 0.3)
            (1,1,1,1,0.1)
        )
        
        with a1:
            generate_rank_region_population("Cherkasy")

        with a2:
            generate_region_total_linechart("Cherkasy")

        with a3:
            generate_region_weapons_polarchart('Cherkasy')
        
        with a4:
            generate_region_report_10y_linechart("Cherkasy")


        # Chernihiv
        b1, b2, b3, b4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with b1:
            generate_rank_region_population("Chernihiv")

        with b2:
            generate_region_total_linechart("Chernihiv")

        with b3:
            generate_region_weapons_polarchart('Chernihiv')
        
        with b4:
            generate_region_report_10y_linechart("Chernihiv")


        # Chernivtsi
        c1, c2, c3, c4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with c1:
            generate_rank_region_population("Chernivtsi")

        with c2:
            generate_region_total_linechart("Chernivtsi")

        with c3:
            generate_region_weapons_polarchart('Chernivtsi')
        
        with c4:
            generate_region_report_10y_linechart("Chernivtsi")


        # Dnipro
        d1, d2, d3, d4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with d1:
            generate_rank_region_population("Dnipro")

        with d2:
            generate_region_total_linechart("Dnipro")

        with d3:
            generate_region_weapons_polarchart('Dnipro')
        
        with d4:
            generate_region_report_10y_linechart("Dnipro")


        # Donetsk
        e1, e2, e3, e4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with e1:
            generate_rank_region_population("Donetsk")

        with e2:
            generate_region_total_linechart("Donetsk")

        with e3:
            generate_region_weapons_polarchart('Donetsk')
        
        with e4:
            generate_region_report_10y_linechart("Donetsk")


        # Ivano-Frankivsk
        f1, f2, f3, f4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with f1:
            generate_rank_region_population("Ivano-Frankivsk")

        with f2:
            generate_region_total_linechart("Ivano-Frankivsk")

        with f3:
            generate_region_weapons_polarchart('Ivano-Frankivsk')
        
        with f4:
            generate_region_report_10y_linechart("Ivano-Frankivsk")


        # Kharkiv
        g1, g2, g3, g4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with g1:
            generate_rank_region_population("Kharkiv")

        with g2:
            generate_region_total_linechart("Kharkiv")

        with g3:
            generate_region_weapons_polarchart('Kharkiv')
        
        with g4:
            generate_region_report_10y_linechart("Kharkiv")


        # Kherson
        h1, h2, h3, h4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with h1:
            generate_rank_region_population("Kherson")

        with h2:
            generate_region_total_linechart("Kherson")

        with h3:
            generate_region_weapons_polarchart('Kherson')
        
        with h4:
            generate_region_report_10y_linechart("Kherson")


        # Khmelnytskyi
        i1, i2, i3, i4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with i1:
            generate_rank_region_population("Khmelnytskyi")

        with i2:
            generate_region_total_linechart("Khmelnytskyi")

        with i3:
            generate_region_weapons_polarchart('Khmelnytskyi')
        
        with i4:
            generate_region_report_10y_linechart("Khmelnytskyi")


        # Kropyvnytskyi
        j1, j2, j3, j4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with j1:
            generate_rank_region_population("Kropyvnytskyi")

        with j2:
            generate_region_total_linechart("Kropyvnytskyi")

        with j3:
            generate_region_weapons_polarchart('Kropyvnytskyi')
        
        with j4:
            generate_region_report_10y_linechart("Kropyvnytskyi")


        # Kyiv
        k1, k2, k3, k4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with k1:
            generate_rank_region_population("Kyiv")

        with k2:
            generate_region_total_linechart("Kyiv")

        with k3:
            generate_region_weapons_polarchart('Kyiv')
        
        with k4:
            generate_region_report_10y_linechart("Kyiv")


        # Luhansk
        l1, l2, l3, l4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with l1:
            generate_rank_region_population("Luhansk")

        with l2:
            generate_region_total_linechart("Luhansk")

        with l3:
            generate_region_weapons_polarchart('Luhansk')
        
        with l4:
            generate_region_report_10y_linechart("Luhansk")


        # Lutsk
        m1, m2, m3, m4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with m1:
            generate_rank_region_population("Lutsk")

        with m2:
            generate_region_total_linechart("Lutsk")

        with m3:
            generate_region_weapons_polarchart('Lutsk')
        
        with m4:
            generate_region_report_10y_linechart("Lutsk")


        # Lviv
        n1, n2, n3, n4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with n1:
            generate_rank_region_population("Lviv")

        with n2:
            generate_region_total_linechart("Lviv")

        with n3:
            generate_region_weapons_polarchart('Lviv')
        
        with n4:
            generate_region_report_10y_linechart("Lviv")


        # Mykolaiv
        o1, o2, o3, o4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with o1:
            generate_rank_region_population("Mykolaiv")

        with o2:
            generate_region_total_linechart("Mykolaiv")

        with o3:
            generate_region_weapons_polarchart('Mykolaiv')
        
        with o4:
            generate_region_report_10y_linechart("Mykolaiv")


        # Odesa
        p1, p2, p3, p4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with p1:
            generate_rank_region_population("Odesa")

        with p2:
            generate_region_total_linechart("Odesa")

        with p3:
            generate_region_weapons_polarchart('Odesa')
        
        with p4:
            generate_region_report_10y_linechart("Odesa")


        # Poltava
        q1, q2, q3, q4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with q1:
            generate_rank_region_population("Poltava")

        with q2:
            generate_region_total_linechart("Poltava")

        with q3:
            generate_region_weapons_polarchart('Poltava')
        
        with q4:
            generate_region_report_10y_linechart("Poltava")


        # Rivne
        r1, r2, r3, r4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with r1:
            generate_rank_region_population("Rivne")

        with r2:
            generate_region_total_linechart("Rivne")

        with r3:
            generate_region_weapons_polarchart('Rivne')
        
        with r4:
            generate_region_report_10y_linechart("Rivne")


        # Simferopol
        s1, s2, s3, s4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with s1:
            generate_rank_region_population("Simferopol")

        with s2:
            generate_region_total_linechart("Simferopol")

        with s3:
            generate_region_weapons_polarchart('Simferopol')
        
        with s4:
            generate_region_report_10y_linechart("Simferopol")


        # Sumy
        t1, t2, t3, t4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with t1:
            generate_rank_region_population("Sumy")

        with t2:
            generate_region_total_linechart("Sumy")

        with t3:
            generate_region_weapons_polarchart('Sumy')
        
        with t4:
            generate_region_report_10y_linechart("Sumy")


        # Ternopil
        u1, u2, u3, u4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with u1:
            generate_rank_region_population("Ternopil")

        with u2:
            generate_region_total_linechart("Ternopil")

        with u3:
            generate_region_weapons_polarchart('Ternopil')
        
        with u4:
            generate_region_report_10y_linechart("Ternopil")


        # Uzhhorod
        v1, v2, v3, v4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with v1:
            generate_rank_region_population("Uzhhorod")

        with v2:
            generate_region_total_linechart("Uzhhorod")

        with v3:
            generate_region_weapons_polarchart('Uzhhorod')
        
        with v4:
            generate_region_report_10y_linechart("Uzhhorod")


        # Vinnytsia
        w1, w2, w3, w4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with w1:
            generate_rank_region_population("Vinnytsia")

        with w2:
            generate_region_total_linechart("Vinnytsia")

        with w3:
            generate_region_weapons_polarchart('Vinnytsia')
        
        with w4:
            generate_region_report_10y_linechart("Vinnytsia")


        # Zaporizhzhia
        x1, x2, x3, x4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with x1:
            generate_rank_region_population("Zaporizhzhia")

        with x2:
            generate_region_total_linechart("Zaporizhzhia")

        with x3:
            generate_region_weapons_polarchart('Zaporizhzhia')
        
        with x4:
            generate_region_report_10y_linechart("Zaporizhzhia")


        # Zhytomyr
        y1, y2, y3, y4, _ = st.columns(
            (1,1,1,1,0.1),
        )
    
        with y1:
            generate_rank_region_population("Zhytomyr")

        with y2:
            generate_region_total_linechart("Zhytomyr")

        with y3:
            generate_region_weapons_polarchart('Zhytomyr')
        
        with y4:
            generate_region_report_10y_linechart("Zhytomyr")
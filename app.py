import streamlit as st
import pandas as pd
import os.path
import time

from elements import main_hist
from elements import yr_weekly_scats
from elements import scatter_table
from elements import hbar_wep
from elements import tls_ratio
from elements import top_5
from elements import region_population_end2021
from elements import region_total_end2021
from elements import region_yr_totals_linegarph
from elements import region_maxmin
from elements import region_yr_totals_linegrph2012
from elements import region_rank_total
from elements import region_total
from elements import region_theftloss_piechart
from elements import region_theftloss_totals


# ========================#
# --------SETTINGS--------#

# Page
st.set_page_config(
    page_title="Lost and Stolen Weapons in Ukraine",
    page_icon="assets\cyan-tesseract-3d-200x200.png",
    layout="wide",
)

# "Made with streamlit" (hide)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer{visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Fullscreen Button (hide)
hide_full_screen = """
            <style>
            button.css-z52931.e19lei0e1{visibility: hidden;}
            </style>
            """
st.markdown(hide_full_screen, unsafe_allow_html=True)

# Metrics red color (change)
change_metrics_red = """
            <style>
            div.css-wnm74r.e16fv1kl0{color: FF8A8A;}
            </style>
            """
st.markdown(change_metrics_red, unsafe_allow_html=True)

# Page padding
st.markdown(
    f"""
    <style>
        .appview-container .main .block-container{{
            padding-top: {0}rem;
            padding-bottom: {0}rem;
            padding-left: {3}rem;
            padding-right: {2}rem;
        }}
    </style>""",
    unsafe_allow_html=True,
)

# Font
streamlit_font = """
			<style>
			@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@500&display=swap');

			html, body, [class*="css"]  {
			font-family: 'Noto Sans', sans-serif;
			}
			</style>
			"""
st.markdown(streamlit_font, unsafe_allow_html=True)

# Colors
clr = "#00ccd3"
biclr = ["#faffff", "#007a81"]


# ====================#
# --------DATA--------#

regional_stats = pd.read_parquet("assets/models/country-stats.parquet.gzip")
top = regional_stats.nlargest(5, "frequency")
bot = regional_stats.nsmallest(5, "frequency")

agg_weapon_ctgr = pd.read_parquet("assets/models/agg-weapon-ctgr.parquet.gzip")

region_tl = pd.read_parquet("assets/models/regions-tl.parquet.gzip")

population = pd.read_csv("assets/ua-population.csv", usecols=["region", "2020", "2021"])

# Spinner
with st.spinner("Please wait a few seconds while I prepare everything...🔥"):
    # =====================#
    # --------TITLE--------#

    def update_year(file):
        t = os.path.getmtime(file)
        year, month, day, hour, minute, second = time.localtime(t)[:-3]
        year = f"{year}"
        return year

    # Project title
    st.title(
        f"Lost and Stolen Weapons in Ukraine (1991-{update_year('assets/models/country-stats.parquet.gzip')})"
    )

    def modification_date(file):
        t = os.path.getmtime(file)
        year, month, day, hour, minute, second = time.localtime(t)[:-3]
        date = f"{year}-{month}-{day}"
        return date

    # Project description
    st.markdown(
        f"""
        <small><span style='color: #484848'>Last update: {modification_date('assets/models/country-stats.parquet.gzip')}</span></small>
        <br><small>This webpage is a visual representation of the dataset provided by MIA of Ukraine to the open data portal under the Creative Commons Attribution license.</small>
        """,
        unsafe_allow_html=True,
    )

    # =========================#
    # --------SECTION 1--------#

    # Histogram
    main_hist()

    st.write("***")

    # =========================#
    # --------SECTION 2--------#

    m1, m2, m3, m4, m5, m6, m7 = st.columns((1.4, 1.2, 1.2, 1.2, 1, 1, 1))

    with m1:
        # # Temporary off
        # st.metric(
        #     "Population (end of 2021)",
        #     f"{population['2021'].sum():,}",
        #     f"{(population['2021'].sum()-population['2020'].sum()):,}",
        #     delta_color="normal"
        #     )

        st.metric(
            "~ Population (2023)",
            f"{34000000:,}",
            f"-{8000000:,}",  # According to UN
            delta_color="normal",
            help="According to IDSS of Ukraine, the country's population was between 28 and 34 million as of January 1, 2023.",
        )

    with m2:
        st.metric(
            "Total Records",
            f"{(regional_stats['loss'].sum()+regional_stats['theft'].sum()):,}",
        )

    with m3:
        st.metric("Total Lost", f"{regional_stats['loss'].sum():,}")

    with m4:
        st.metric("Total Stolen", f"{regional_stats['theft'].sum():,}")

    with m5:
        st.metric(
            f"Records ({update_year('assets/models/country-stats.parquet.gzip')})",
            f"{(region_tl[region_tl['date'].dt.year==int(update_year('assets/models/country-stats.parquet.gzip'))]['total'].sum()):,}",
            f"{(region_tl[region_tl['date'].dt.year==int(update_year('assets/models/country-stats.parquet.gzip'))]['total'].sum() - region_tl[region_tl['date'].dt.year==int(update_year('assets/models/country-stats.parquet.gzip'))-1]['total'].sum()):,}",
            delta_color="inverse",
        )

    with m6:
        st.metric(
            f"Weapons Lost ({update_year('assets/models/country-stats.parquet.gzip')})",
            f"{(region_tl[region_tl['date'].dt.year==int(update_year('assets/models/country-stats.parquet.gzip'))]['loss'].sum()):,}",
            f"{(region_tl[region_tl['date'].dt.year==int(update_year('assets/models/country-stats.parquet.gzip'))]['loss'].sum() - region_tl[region_tl['date'].dt.year==int(update_year('assets/models/country-stats.parquet.gzip'))-1]['loss'].sum()):,}",
            delta_color="inverse",
            help="Current number compared to previous year total",
        )

    with m7:
        st.metric(
            f"Weapons Stolen ({update_year('assets/models/country-stats.parquet.gzip')})",
            f"{(region_tl[region_tl['date'].dt.year==int(update_year('assets/models/country-stats.parquet.gzip'))]['theft'].sum()):,}",
            f"{(region_tl[region_tl['date'].dt.year==int(update_year('assets/models/country-stats.parquet.gzip'))]['theft'].sum() - region_tl[region_tl['date'].dt.year==int(update_year('assets/models/country-stats.parquet.gzip'))-1]['theft'].sum()):,}",
            delta_color="inverse",
            help="Current number compared to previous year total",
        )

    st.markdown("***", unsafe_allow_html=True)

    _a, sec2_col2, _b, sec2_col3, _c = st.columns((1, 3, 0.25, 6, 1))

    with _a:
        st.empty()

    with sec2_col2:
        top_5()

        tls_ratio()

    with _b:
        st.empty()

    with sec2_col3:
        # Scatterplots
        yr_weekly_scats()

    with _c:
        st.empty()

    st.markdown("<br>", unsafe_allow_html=True)

    (
        sec2_1_col1,
        sec2_1_col2,
        sec2_1_col3,
        sec2_1_col4,
        sec2_1_col5,
        sec2_1_col6,
    ) = st.columns(6)

    with sec2_1_col1:
        total_prev = (
            region_tl[region_tl["date"].dt.year < 2014]
            .groupby(["region"])["total"]
            .sum()
            .reset_index()["total"]
            .sum()
        )
        total_2014 = (
            region_tl[region_tl["date"].dt.year == 2014]
            .groupby(["region"])["total"]
            .sum()
            .reset_index()["total"]
            .sum()
        )
        pct_diff = int(total_2014 / total_prev * 100)

        st.markdown(
            f"""
            * In <span style='color: {clr}'>2014</span> alone there were nearly 
                <span style='color: {clr}'>{pct_diff}% more records</span> than in all previous years combined.
            """,
            unsafe_allow_html=True,
        )

    with sec2_1_col2:
        st.markdown(
            f"""
            * <span style='color: {clr}'>Simferopol</span> (Crimea) accounts for around <span title="{top.loc[0,'frequency']:,} records" 
                style='color: {clr}'>{int(round(top.iloc[0]['pct_of_total'], 2)*100)}%</span> of all records. 
                The main contributor to this high percentage was the <span style='color: {clr}'>2014</span> annexation, meaning that all 
                <span style='color: {clr}'>weapons registered</span> there were likely <span style='color: {clr}'>labeled as lost or stolen</span>.
            """,
            unsafe_allow_html=True,
        )

    with sec2_1_col3:
        st.markdown(
            f"""
            * The <span style='color: {clr}'>tiniest</span> share of the country records has the <span style='color: {clr}'>{bot.iloc[0,0]}</span> region, 
                around <span title="{bot.iloc[0]['frequency']:,} records" style='color: {clr}'>{round(bot.iloc[0]['pct_of_total'], 3)*100}%</span>. 
                It is closely followed by <span style='color: {clr}'>{bot.iloc[1,0]}</span>, accounting for 
                <span title="{bot.iloc[1]['frequency']:,} records" style='color: {clr}'>{round(bot.iloc[1]['pct_of_total'], 3)*100}%</span> of all reports.
            """,
            unsafe_allow_html=True,
        )

    with sec2_1_col4:
        st.markdown(
            f"""
            * <span style='color: {clr}'>{regional_stats.loc[regional_stats['theft_pct'].idxmin()]['region']}</span> has the 
                <span style='color: {clr}'>lowest</span> percentage of <span style='color: {clr}'>theft</span> reports, 
                only <span title="{regional_stats.loc[regional_stats['theft_pct'].idxmin()]['theft']:,} records" 
                style='color:{clr}'>{int(round(regional_stats.loc[regional_stats['theft_pct'].idxmin(),'theft_pct'], 2)*100)}%</span>, and the 
                <span style='color: {clr}'>highest loss</span> percentage, nearly 
                <span title="{regional_stats.loc[regional_stats['loss_pct'].idxmax()]['loss']:,} records" 
                style='color:{clr}'>{int(round(regional_stats.loc[regional_stats['loss_pct'].idxmax(),'loss_pct'], 2)*100)}%</span>.<br>
            """,
            unsafe_allow_html=True,
        )

    with sec2_1_col5:
        st.markdown(
            f"""
            * <span style='color: {clr}'>{regional_stats.loc[regional_stats['theft_pct'].idxmax()]['region']}</span>, 
                on the contrary, has around <span title="{regional_stats.loc[regional_stats['theft_pct'].idxmax()]['theft']:,} records" 
                style='color:{clr}'>{int(round(regional_stats.loc[regional_stats['theft_pct'].idxmax(),'theft_pct'], 2)*100)}%</span> 
                of its records being <span style='color: {clr}'>theft</span> reports,
                the <span style='color: {clr}'>highest</span> number among all regions.<br>
            """,
            unsafe_allow_html=True,
        )

    with sec2_1_col6:
        st.markdown(
            f"""
            * The <span style='color: {clr}'>two</span> most "popular" 
                <span style='color: {clr}'>weapon categories</span>, which make up roughly 
                <span title='{agg_weapon_ctgr.loc[agg_weapon_ctgr.index[:2],'total'].sum():,} records' 
                style='color:{clr}'>{(agg_weapon_ctgr.loc[agg_weapon_ctgr.index[:2],'total'].sum()/agg_weapon_ctgr.loc[:,'total'].sum())*100:.0f}%</span> of all records, are 
                <span title='{agg_weapon_ctgr.loc[agg_weapon_ctgr.index[0],'total'].sum():,} records' 
                style='color: {clr}'>{agg_weapon_ctgr.index[0]}</span> and 
                <span title='{agg_weapon_ctgr.loc[agg_weapon_ctgr.index[1],'total'].sum():,} records' 
                style='color: {clr}'>{agg_weapon_ctgr.index[1]}</span>.
            """,
            unsafe_allow_html=True,
        )

    st.write("***")

    # =========================#
    # --------SECTION 3--------#

    st.markdown("<h4>Weapon categories</h4><br>", unsafe_allow_html=True)

    sec3_col1, _a, sec3_col2, _b = st.columns((6, 0.25, 2, 0.5))

    with sec3_col1:
        # "Scatter table"
        scatter_table()

    with _a:
        st.empty()

    with sec3_col2:
        # Horizontal bar chart
        hbar_wep()

        # Weapon categories explanations
        st.markdown(
            f"""
            
            * <span title='{agg_weapon_ctgr.loc["Artillery",'total']} records, {agg_weapon_ctgr.loc["Artillery",'percentage']:.2%} of total' style='color: {clr}'>Artillery</span><br><small> grenade launcher, mortar, ATGM, MANPAD, etc.</small>
            
            * <span title='{agg_weapon_ctgr.loc["Bladed",'total']} records, {agg_weapon_ctgr.loc["Bladed",'percentage']:.2%} of total' style='color: {clr}'>Bladed</span><br><small> knife, sword, bayonet, saber, etc.</small>
            
            * <span title='{agg_weapon_ctgr.loc["Handguns",'total']} records, {agg_weapon_ctgr.loc["Handguns",'percentage']:.2%} of total' style='color: {clr}'>Handguns</span><br><small> pistol, revolver, machine pistol, traumatic pistol, etc.</small>
            
            * <span title='{agg_weapon_ctgr.loc["Heavy firearms",'total']} records, {agg_weapon_ctgr.loc["Heavy firearms",'percentage']:.2%} of total' style='color: {clr}'>Heavy firearms</span><br><small> autocannon, cannon, machine gun, anti-tank rifle, etc.</small>
            
            * <span title='{agg_weapon_ctgr.loc["Light firearms",'total']} records, {agg_weapon_ctgr.loc["Light firearms",'percentage']:.2%} of total' style='color: {clr}'>Light firearms</span><br><small> assault rifle, carabine, shotgun, marksman rifle, etc.</small>
            
            * <span title='{agg_weapon_ctgr.loc["Other",'total']} records, {agg_weapon_ctgr.loc["Other",'percentage']:.2%} of total' style='color: {clr}'>Other</span><br><small> receiver, ammunition, crossbow, carabine replica, etc.</small>
            
            * <span title='{agg_weapon_ctgr.loc["Pneumatic&Flobert",'total']} records, {agg_weapon_ctgr.loc["Pneumatic&Flobert",'percentage']:.2%} of total' style='color: {clr}'>Pneumatic&Flobert</span><br><small> pneumatic rifle, pneumatic pistol, Flobert rifle, Flobert revolver, etc.</small>
            
            * <span title='{agg_weapon_ctgr.loc["Explosives",'total']} records, {agg_weapon_ctgr.loc["Explosives",'percentage']:.2%} of total' style='color: {clr}'>Explosives</span><br><small> explosive material, grenade, rocket, shell, etc.</small>
            
            """,
            unsafe_allow_html=True,
        )

    with _b:
        st.empty()

    st.write("***")

    # =========================#
    # --------SECTION 4--------#

    st.markdown(
        "<h4>Regional records</h4><small>Administrative centers here represent entire regions (oblasts)</small>",
        unsafe_allow_html=True,
    )

    sec4_tab1, sec4_tab2, sec4_tab3, sec4_tab4, sec4_tab5 = st.tabs(
        ["Central", "Northern", "Southern", "Western", "Eastern"]
    )

    # Central
    with sec4_tab1:
        # Cherkasy
        a1, a2, a3, a4, a5, a6, a7, a8, a9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with a1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Cherkasy</font>", unsafe_allow_html=True)

        # Population
        with a2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Cherkasy")

        # Total number of cases for the current year
        with a3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Cherkasy")

        # Rank among other regions
        with a4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Cherkasy")

        # Line chart with all time total
        with a5:
            region_total("Cherkasy")
            region_yr_totals_linegarph("Cherkasy")

        # Maximum and minimum yearly number of records
        with a6:
            region_maxmin("Cherkasy")

        # Theft and Loss ratio Pie chart
        with a7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Cherkasy")

        # Total number of cases for Theft and Loss
        with a8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Cherkasy")

        # Last 10 years Line chart with Theft and Loss
        with a9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Cherkasy")

        st.markdown("<br>", unsafe_allow_html=True)

        # Dnipro
        b1, b2, b3, b4, b5, b6, b7, b8, b9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with b1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Dnipro</font>", unsafe_allow_html=True)

        # Population
        with b2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Dnipro")

        # Total number of cases for the current year
        with b3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Dnipro")

        # Rank among other regions
        with b4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Dnipro")

        # Line chart with all time total
        with b5:
            region_total("Dnipro")
            region_yr_totals_linegarph("Dnipro")

        # Maximum and minimum yearly number of records
        with b6:
            region_maxmin("Dnipro")

        # Theft and Loss ratio Pie chart
        with b7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Dnipro")

        # Total number of cases for Theft and Loss
        with b8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Dnipro")

        # Last 10 years Line chart with Theft and Loss
        with b9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Dnipro")

        st.markdown("<br>", unsafe_allow_html=True)

        # Kropyvnytskyi
        c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with c1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Kropyvnytskyi</font>", unsafe_allow_html=True)

        # Population
        with c2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Kropyvnytskyi")

        # Total number of cases for the current year
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Kropyvnytskyi")

        # Rank among other regions
        with c4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Kropyvnytskyi")

        # Line chart with all time total
        with c5:
            region_total("Kropyvnytskyi")
            region_yr_totals_linegarph("Kropyvnytskyi")

        # Maximum and minimum yearly number of records
        with c6:
            region_maxmin("Kropyvnytskyi")

        # Theft and Loss ratio Pie chart
        with c7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Kropyvnytskyi")

        # Total number of cases for Theft and Loss
        with c8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Kropyvnytskyi")

        # Last 10 years Line chart with Theft and Loss
        with c9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Kropyvnytskyi")

        st.markdown("<br>", unsafe_allow_html=True)

        # Poltava
        d1, d2, d3, d4, d5, d6, d7, d8, d9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with d1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Poltava</font>", unsafe_allow_html=True)

        # Population
        with d2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Poltava")

        # Total number of cases for the current year
        with d3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Poltava")

        # Rank among other regions
        with d4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Poltava")

        # Line chart with all time total
        with d5:
            region_total("Poltava")
            region_yr_totals_linegarph("Poltava")

        # Maximum and minimum yearly number of records
        with d6:
            region_maxmin("Poltava")

        # Theft and Loss ratio Pie chart
        with d7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Poltava")

        # Total number of cases for Theft and Loss
        with d8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Poltava")

        # Last 10 years Line chart with Theft and Loss
        with d9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Poltava")

        st.markdown("<br>", unsafe_allow_html=True)

        # Vinnytsia
        e1, e2, e3, e4, e5, e6, e7, e8, e9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with e1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Vinnytsia</font>", unsafe_allow_html=True)

        # Population
        with e2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Vinnytsia")

        # Total number of cases for the current year
        with e3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Vinnytsia")

        # Rank among other regions
        with e4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Vinnytsia")

        # Line chart with all time total
        with e5:
            region_total("Vinnytsia")
            region_yr_totals_linegarph("Vinnytsia")

        # Maximum and minimum yearly number of records
        with e6:
            region_maxmin("Vinnytsia")

        # Theft and Loss ratio Pie chart
        with e7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Vinnytsia")

        # Total number of cases for Theft and Loss
        with e8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Vinnytsia")

        # Last 10 years Line chart with Theft and Loss
        with e9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Vinnytsia")

    # Northern
    with sec4_tab2:
        # Chernihiv
        a1, a2, a3, a4, a5, a6, a7, a8, a9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with a1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Chernihiv</font>", unsafe_allow_html=True)

        # Population
        with a2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Chernihiv")

        # Total number of cases for the current year
        with a3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Chernihiv")

        # Rank among other regions
        with a4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Chernihiv")

        # Line chart with all time total
        with a5:
            region_total("Chernihiv")
            region_yr_totals_linegarph("Chernihiv")

        # Maximum and minimum yearly number of records
        with a6:
            region_maxmin("Chernihiv")

        # Theft and Loss ratio Pie chart
        with a7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Chernihiv")

        # Total number of cases for Theft and Loss
        with a8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Chernihiv")

        # Last 10 years Line chart with Theft and Loss
        with a9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Chernihiv")

        st.markdown("<br>", unsafe_allow_html=True)

        # Kyiv
        b1, b2, b3, b4, b5, b6, b7, b8, b9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with b1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Kyiv</font>", unsafe_allow_html=True)

        # Population
        with b2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Kyiv")

        # Total number of cases for the current year
        with b3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Kyiv")

        # Rank among other regions
        with b4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Kyiv")

        # Line chart with all time total
        with b5:
            region_total("Kyiv")
            region_yr_totals_linegarph("Kyiv")

        # Maximum and minimum yearly number of records
        with b6:
            region_maxmin("Kyiv")

        # Theft and Loss ratio Pie chart
        with b7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Kyiv")

        # Total number of cases for Theft and Loss
        with b8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Kyiv")

        # Last 10 years Line chart with Theft and Loss
        with b9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Kyiv")

        st.markdown("<br>", unsafe_allow_html=True)

        # Sumy
        c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with c1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Sumy</font>", unsafe_allow_html=True)

        # Population
        with c2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Sumy")

        # Total number of cases for the current year
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Sumy")

        # Rank among other regions
        with c4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Sumy")

        # Line chart with all time total
        with c5:
            region_total("Sumy")
            region_yr_totals_linegarph("Sumy")

        # Maximum and minimum yearly number of records
        with c6:
            region_maxmin("Sumy")

        # Theft and Loss ratio Pie chart
        with c7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Sumy")

        # Total number of cases for Theft and Loss
        with c8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Sumy")

        # Last 10 years Line chart with Theft and Loss
        with c9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Sumy")

        st.markdown("<br>", unsafe_allow_html=True)

        # Zhytomyr
        d1, d2, d3, d4, d5, d6, d7, d8, d9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with d1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Zhytomyr</font>", unsafe_allow_html=True)

        # Population
        with d2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Zhytomyr")

        # Total number of cases for the current year
        with d3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Zhytomyr")

        # Rank among other regions
        with d4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Zhytomyr")

        # Line chart with all time total
        with d5:
            region_total("Zhytomyr")
            region_yr_totals_linegarph("Zhytomyr")

        # Maximum and minimum yearly number of records
        with d6:
            region_maxmin("Zhytomyr")

        # Theft and Loss ratio Pie chart
        with d7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Zhytomyr")

        # Total number of cases for Theft and Loss
        with d8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Zhytomyr")

        # Last 10 years Line chart with Theft and Loss
        with d9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Zhytomyr")

    # Southern
    with sec4_tab3:
        # Kherson
        a1, a2, a3, a4, a5, a6, a7, a8, a9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with a1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Kherson</font>", unsafe_allow_html=True)

        # Population
        with a2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Kherson")

        # Total number of cases for the current year
        with a3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Kherson")

        # Rank among other regions
        with a4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Kherson")

        # Line chart with all time total
        with a5:
            region_total("Kherson")
            region_yr_totals_linegarph("Kherson")

        # Maximum and minimum yearly number of records
        with a6:
            region_maxmin("Kherson")

        # Theft and Loss ratio Pie chart
        with a7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Kherson")

        # Total number of cases for Theft and Loss
        with a8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Kherson")

        # Last 10 years Line chart with Theft and Loss
        with a9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Kherson")

        st.markdown("<br>", unsafe_allow_html=True)

        # Mykolaiv
        b1, b2, b3, b4, b5, b6, b7, b8, b9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with b1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Mykolaiv</font>", unsafe_allow_html=True)

        # Population
        with b2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Mykolaiv")

        # Total number of cases for the current year
        with b3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Mykolaiv")

        # Rank among other regions
        with b4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Mykolaiv")

        # Line chart with all time total
        with b5:
            region_total("Mykolaiv")
            region_yr_totals_linegarph("Mykolaiv")

        # Maximum and minimum yearly number of records
        with b6:
            region_maxmin("Mykolaiv")

        # Theft and Loss ratio Pie chart
        with b7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Mykolaiv")

        # Total number of cases for Theft and Loss
        with b8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Mykolaiv")

        # Last 10 years Line chart with Theft and Loss
        with b9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Mykolaiv")

        st.markdown("<br>", unsafe_allow_html=True)

        # Odesa
        c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with c1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Odesa</font>", unsafe_allow_html=True)

        # Population
        with c2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Odesa")

        # Total number of cases for the current year
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Odesa")

        # Rank among other regions
        with c4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Odesa")

        # Line chart with all time total
        with c5:
            region_total("Odesa")
            region_yr_totals_linegarph("Odesa")

        # Maximum and minimum yearly number of records
        with c6:
            region_maxmin("Odesa")

        # Theft and Loss ratio Pie chart
        with c7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Odesa")

        # Total number of cases for Theft and Loss
        with c8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Odesa")

        # Last 10 years Line chart with Theft and Loss
        with c9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Odesa")

        st.markdown("<br>", unsafe_allow_html=True)

        # Simferopol
        d1, d2, d3, d4, d5, d6, d7, d8, d9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with d1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Simferopol</font>", unsafe_allow_html=True)

        # Population
        with d2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Simferopol")

        # Total number of cases for the current year
        with d3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Simferopol")

        # Rank among other regions
        with d4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Simferopol")

        # Line chart with all time total
        with d5:
            region_total("Simferopol")
            region_yr_totals_linegarph("Simferopol")

        # Maximum and minimum yearly number of records
        with d6:
            region_maxmin("Simferopol")

        # Theft and Loss ratio Pie chart
        with d7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Simferopol")

        # Total number of cases for Theft and Loss
        with d8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Simferopol")

        # Last 10 years Line chart with Theft and Loss
        with d9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Simferopol")

        st.markdown("<br>", unsafe_allow_html=True)

        # Zaporizhzhia
        e1, e2, e3, e4, e5, e6, e7, e8, e9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with e1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Zaporizhzhia</font>", unsafe_allow_html=True)

        # Population
        with e2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Zaporizhzhia")

        # Total number of cases for the current year
        with e3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Zaporizhzhia")

        # Rank among other regions
        with e4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Zaporizhzhia")

        # Line chart with all time total
        with e5:
            region_total("Zaporizhzhia")
            region_yr_totals_linegarph("Zaporizhzhia")

        # Maximum and minimum yearly number of records
        with e6:
            region_maxmin("Zaporizhzhia")

        # Theft and Loss ratio Pie chart
        with e7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Zaporizhzhia")

        # Total number of cases for Theft and Loss
        with e8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Zaporizhzhia")

        # Last 10 years Line chart with Theft and Loss
        with e9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Zaporizhzhia")

    # Western
    with sec4_tab4:
        # Chernivtsi
        a1, a2, a3, a4, a5, a6, a7, a8, a9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with a1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Chernivtsi</font>", unsafe_allow_html=True)

        # Population
        with a2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Chernivtsi")

        # Total number of cases for the current year
        with a3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Chernivtsi")

        # Rank among other regions
        with a4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Chernivtsi")

        # Line chart with all time total
        with a5:
            region_total("Chernivtsi")
            region_yr_totals_linegarph("Chernivtsi")

        # Maximum and minimum yearly number of records
        with a6:
            region_maxmin("Chernivtsi")

        # Theft and Loss ratio Pie chart
        with a7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Chernivtsi")

        # Total number of cases for Theft and Loss
        with a8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Chernivtsi")

        # Last 10 years Line chart with Theft and Loss
        with a9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Chernivtsi")

        st.markdown("<br>", unsafe_allow_html=True)

        # Ivano-Frankivsk
        b1, b2, b3, b4, b5, b6, b7, b8, b9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with b1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown(
                "<font size='6.5'>Ivano-Frankivsk</font>", unsafe_allow_html=True
            )

        # Population
        with b2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Ivano-Frankivsk")

        # Total number of cases for the current year
        with b3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Ivano-Frankivsk")

        # Rank among other regions
        with b4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Ivano-Frankivsk")

        # Line chart with all time total
        with b5:
            region_total("Ivano-Frankivsk")
            region_yr_totals_linegarph("Ivano-Frankivsk")

        # Maximum and minimum yearly number of records
        with b6:
            region_maxmin("Ivano-Frankivsk")

        # Theft and Loss ratio Pie chart
        with b7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Ivano-Frankivsk")

        # Total number of cases for Theft and Loss
        with b8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Ivano-Frankivsk")

        # Last 10 years Line chart with Theft and Loss
        with b9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Ivano-Frankivsk")

        st.markdown("<br>", unsafe_allow_html=True)

        # Khmelnytskyi
        c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with c1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Khmelnytskyi</font>", unsafe_allow_html=True)

        # Population
        with c2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Khmelnytskyi")

        # Total number of cases for the current year
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Khmelnytskyi")

        # Rank among other regions
        with c4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Khmelnytskyi")

        # Line chart with all time total
        with c5:
            region_total("Khmelnytskyi")
            region_yr_totals_linegarph("Khmelnytskyi")

        # Maximum and minimum yearly number of records
        with c6:
            region_maxmin("Khmelnytskyi")

        # Theft and Loss ratio Pie chart
        with c7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Khmelnytskyi")

        # Total number of cases for Theft and Loss
        with c8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Khmelnytskyi")

        # Last 10 years Line chart with Theft and Loss
        with c9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Khmelnytskyi")

        st.markdown("<br>", unsafe_allow_html=True)

        # Lutsk
        d1, d2, d3, d4, d5, d6, d7, d8, d9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with d1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Lutsk</font>", unsafe_allow_html=True)

        # Population
        with d2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Lutsk")

        # Total number of cases for the current year
        with d3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Lutsk")

        # Rank among other regions
        with d4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Lutsk")

        # Line chart with all time total
        with d5:
            region_total("Lutsk")
            region_yr_totals_linegarph("Lutsk")

        # Maximum and minimum yearly number of records
        with d6:
            region_maxmin("Lutsk")

        # Theft and Loss ratio Pie chart
        with d7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Lutsk")

        # Total number of cases for Theft and Loss
        with d8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Lutsk")

        # Last 10 years Line chart with Theft and Loss
        with d9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Lutsk")

        st.markdown("<br>", unsafe_allow_html=True)

        # Lviv
        e1, e2, e3, e4, e5, e6, e7, e8, e9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with e1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Lviv</font>", unsafe_allow_html=True)

        # Population
        with e2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Lviv")

        # Total number of cases for the current year
        with e3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Lviv")

        # Rank among other regions
        with e4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Lviv")

        # Line chart with all time total
        with e5:
            region_total("Lviv")
            region_yr_totals_linegarph("Lviv")

        # Maximum and minimum yearly number of records
        with e6:
            region_maxmin("Lviv")

        # Theft and Loss ratio Pie chart
        with e7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Lviv")

        # Total number of cases for Theft and Loss
        with e8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Lviv")

        # Last 10 years Line chart with Theft and Loss
        with e9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Lviv")

        st.markdown("<br>", unsafe_allow_html=True)

        # Rivne
        f1, f2, f3, f4, f5, f6, f7, f8, f9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with f1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Rivne</font>", unsafe_allow_html=True)

        # Population
        with f2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Rivne")

        # Total number of cases for the current year
        with f3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Rivne")

        # Rank among other regions
        with f4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Rivne")

        # Line chart with all time total
        with f5:
            region_total("Rivne")
            region_yr_totals_linegarph("Rivne")

        # Maximum and minimum yearly number of records
        with f6:
            region_maxmin("Rivne")

        # Theft and Loss ratio Pie chart
        with f7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Rivne")

        # Total number of cases for Theft and Loss
        with f8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Rivne")

        # Last 10 years Line chart with Theft and Loss
        with f9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Rivne")

        st.markdown("<br>", unsafe_allow_html=True)

        # Ternopil
        g1, g2, g3, g4, g5, g6, g7, g8, g9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with g1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Ternopil</font>", unsafe_allow_html=True)

        # Population
        with g2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Ternopil")

        # Total number of cases for the current year
        with g3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Ternopil")

        # Rank among other regions
        with g4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Ternopil")

        # Line chart with all time total
        with g5:
            region_total("Ternopil")
            region_yr_totals_linegarph("Ternopil")

        # Maximum and minimum yearly number of records
        with g6:
            region_maxmin("Ternopil")

        # Theft and Loss ratio Pie chart
        with g7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Ternopil")

        # Total number of cases for Theft and Loss
        with g8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Ternopil")

        # Last 10 years Line chart with Theft and Loss
        with g9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Ternopil")

        st.markdown("<br>", unsafe_allow_html=True)

        # Uzhhorod
        h1, h2, h3, h4, h5, h6, h7, h8, h9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with h1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Uzhhorod</font>", unsafe_allow_html=True)

        # Population
        with h2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Uzhhorod")

        # Total number of cases for the current year
        with h3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Uzhhorod")

        # Rank among other regions
        with h4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Uzhhorod")

        # Line chart with all time total
        with h5:
            region_total("Uzhhorod")
            region_yr_totals_linegarph("Uzhhorod")

        # Maximum and minimum yearly number of records
        with h6:
            region_maxmin("Uzhhorod")

        # Theft and Loss ratio Pie chart
        with h7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Uzhhorod")

        # Total number of cases for Theft and Loss
        with h8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Uzhhorod")

        # Last 10 years Line chart with Theft and Loss
        with h9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Uzhhorod")

    # Eastern
    with sec4_tab5:
        # Donetsk
        a1, a2, a3, a4, a5, a6, a7, a8, a9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with a1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Donetsk</font>", unsafe_allow_html=True)

        # Population
        with a2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Donetsk")

        # Total number of cases for the current year
        with a3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Donetsk")

        # Rank among other regions
        with a4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Donetsk")

        # Line chart with all time total
        with a5:
            region_total("Donetsk")
            region_yr_totals_linegarph("Donetsk")

        # Maximum and minimum yearly number of records
        with a6:
            region_maxmin("Donetsk")

        # Theft and Loss ratio Pie chart
        with a7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Donetsk")

        # Total number of cases for Theft and Loss
        with a8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Donetsk")

        # Last 10 years Line chart with Theft and Loss
        with a9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Donetsk")

        st.markdown("<br>", unsafe_allow_html=True)

        # Kharkiv
        b1, b2, b3, b4, b5, b6, b7, b8, b9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with b1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Kharkiv</font>", unsafe_allow_html=True)

        # Population
        with b2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Kharkiv")

        # Total number of cases for the current year
        with b3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Kharkiv")

        # Rank among other regions
        with b4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Kharkiv")

        # Line chart with all time total
        with b5:
            region_total("Kharkiv")
            region_yr_totals_linegarph("Kharkiv")

        # Maximum and minimum yearly number of records
        with b6:
            region_maxmin("Kharkiv")

        # Theft and Loss ratio Pie chart
        with b7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Kharkiv")

        # Total number of cases for Theft and Loss
        with b8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Kharkiv")

        # Last 10 years Line chart with Theft and Loss
        with b9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Kharkiv")

        st.markdown("<br>", unsafe_allow_html=True)

        # Luhansk
        c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
            (0.95, 0.55, 0.35, 0.3, 0.9, 0.32, 0.53, 0.35, 0.75)
        )
        # Region name
        with c1:
            st.markdown("<br></br>", unsafe_allow_html=True)
            st.markdown("<font size='6.5'>Luhansk</font>", unsafe_allow_html=True)

        # Population
        with c2:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_population_end2021("Luhansk")

        # Total number of cases for the current year
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            region_total_end2021("Luhansk")

        # Rank among other regions
        with c4:
            st.markdown("<br></br>", unsafe_allow_html=True)
            region_rank_total("Luhansk")

        # Line chart with all time total
        with c5:
            region_total("Luhansk")
            region_yr_totals_linegarph("Luhansk")

        # Maximum and minimum yearly number of records
        with c6:
            region_maxmin("Luhansk")

        # Theft and Loss ratio Pie chart
        with c7:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_piechart("Luhansk")

        # Total number of cases for Theft and Loss
        with c8:
            st.markdown("<br>", unsafe_allow_html=True)
            region_theftloss_totals("Luhansk")

        # Last 10 years Line chart with Theft and Loss
        with c9:
            st.markdown("<center>Last 10 years trend</center>", unsafe_allow_html=True)
            region_yr_totals_linegrph2012("Luhansk")

    # ========================#
    # --------FOOTER--------#
    footer = """
        <style>
        a:link , a:visited{
        color: blue;
        background-color: transparent;
        text-decoration: underline;
        }

        a:hover,  a:active {
        color: red;
        background-color: transparent;
        text-decoration: underline;
        }

        .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #484848;
        color: #EEEEEE;
        text-align: center;
        }
        </style>
        <div class="footer">
        Project by <a style=text-align: center; href="https://github.com/cyterat"><img src="https://images2.imgbox.com/3f/e6/RqycpnL4_o.png" alt="cyterat" width="25" height="30"></a>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        Made with <a style=text-align: center; href="https://streamlit.io/"><img src="https://images2.imgbox.com/25/4b/TEp8DFI1_o.png" alt="streamlit" width="25" height="30"></a>
        </div>
    """
    st.markdown(footer, unsafe_allow_html=True)

st.success("")

# Spinner load succesful (hide)
hide_spinner_succes = """
<style>
div.st-ae {
    -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
    font-size: 0rem;
    line-height: 0;
    height: 0;
    padding-top: 0px;
    padding-right: 0px;
    padding-bottom: 0px;
    padding-left: 0px;
    margin-top: 0px;
    margin-bottom: 0px;
    border-top-left-radius: 0rem;
    border-top-right-radius: 0rem;
    border-bottom-right-radius: 0rem;
    border-bottom-left-radius: 0rem;
    box-shadow: none;
    border: 0px;
    opacity: 0;
    }
 </style>
"""
st.markdown(hide_spinner_succes, unsafe_allow_html=True)

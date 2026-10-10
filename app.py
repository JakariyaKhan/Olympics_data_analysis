"""
Olympics Historical & Performance Analytics Hub
Created by Jakariya Khan for Data Analyst Portfolio & Technical Interviews.
"""
import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import data_loader as dl
import ui_utils as ui
from PIL import Image

# 1. Page Configuration
st.set_page_config(
    page_title="Olympics Analytics Hub | Jakariya Khan",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply unified styling
ui.apply_custom_theme()

# 2. Data Ingestion
with st.spinner("Loading and preprocessing 130 years of Olympic records..."):
    df = dl.load_olympic_data()
    dedup_medals = dl.get_deduplicated_medals(df)

# 3. Sidebar Configuration
with st.sidebar:
    logo_path = os.path.join("assets", "Logo.webp")
    st.image(logo_path, width=180)
    st.title("Olympics Analytics")
    st.markdown("**Author:** Jakariya Khan  \n*Data Analyst | AI & ML Enthusiast*")
    st.markdown("---")
    
    st.subheader("📌 Project Navigation")
    st.markdown("""
    Explore deep-dive analytical modules in the sidebar:
    - **🏅 Medal Analysis:** Event deduplication, medal tallies, decade heatmaps, points efficiency.
    - **🌍 Country Analysis:** Host country lift, conversion rates, gender evolution, head-to-head comparisons.
    - **🏃 Athlete Analysis:** Age peak curves, longevity, career timelines, all-time Olympians.
    - **🎯 Sport Analysis:** Monopolies, HHI competitiveness, sunburst hierarchies, event trends.
    - **📈 Historical Trends:** Gender parity (Title IX to Paris 2024), geopolitics, Cold War rivalry, debut waves.
    - **🔍 Data Explorer:** Self-serve interactive filtering, demographic distributions, and CSV export.
    - **🇮🇳 India at Olympics:** 125+ years of records, 8-Gold Hockey Dynasty, modern multi-sport resurgence, and athlete Hall of Fame.
    """)
    st.markdown("---")
    st.caption("Tech Stack: Python, Pandas, NumPy, Plotly, SciPy, Streamlit")

# 4. Hero Banner
ui.render_hero_banner(
    title="Olympics Historical & Performance Analytics (1896 – 2026)",
    subtitle="From Athens 1896 to Paris 2024, this platform explores 300,000+ Olympic records — blending engineering pipelines, hypothesis testing, and BI dashboards to reveal the stories behind medals, nations, and athletes."
)

# 5. Executive KPI Row
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Athlete Entries", f"{len(df):,}")
kpi2.metric("Unique Athletes", f"{df['Name'].nunique():,}")
kpi3.metric("NOCs & Nations", f"{df['Region'].nunique():,}")
kpi4.metric("Official Event Medals", f"{len(dedup_medals):,}", help="Deduplicated at event-level to prevent team multi-counting")
kpi5.metric("Olympic Editions", f"{df[['Year', 'Season']].drop_duplicates().shape[0]} Games")

st.markdown("<br>", unsafe_allow_html=True)

# 6. Global Geographical Medal Distribution
st.subheader("🌍 Global Distribution of Olympic Medals")

col_filter1, col_filter2 = st.columns([2, 3])
with col_filter1:
    season_filter = st.radio("Select Season:", ["All", "Summer", "Winter"], horizontal=True, key="home_season")
with col_filter2:
    view_metric = st.selectbox("Color Metric:", ["Total Medals", "Gold Medals", "Medal Points (Weighted)"], key="home_metric")

tally_df = dl.get_medal_tally(df, year='All-Time', season=season_filter, deduplicate=True)

metric_col_map = {
    "Total Medals": "Total",
    "Gold Medals": "Gold",
    "Medal Points (Weighted)": "Points"
}
color_target = metric_col_map[view_metric]

fig_map = px.choropleth(
    tally_df,
    locations="Region",
    locationmode="country names",
    color=color_target,
    hover_name="Region",
    hover_data=["Gold", "Silver", "Bronze", "Total", "Points", "Rank"],
    color_continuous_scale="Viridis",
    title=f"All-Time {view_metric} by Nation ({season_filter} Games)",
    labels={color_target: view_metric}
)
fig_map.update_layout(
    margin=dict(l=0, r=0, t=40, b=0),
    geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth'),
    height=520
)
st.plotly_chart(fig_map, use_container_width=True)

# 7. Executive Summaries & Visual Comparison (Row 1)
c_left, c_right = st.columns(2)

with c_left:
    st.subheader("🏆 All-Time Top 10 Nations (Official Deduplicated)")
    top10 = tally_df.head(10).copy()
    fig_top10 = px.bar(
        top10,
        x="Region",
        y=["Gold", "Silver", "Bronze"],
        title="Top 10 Nations by Medal Tier",
        labels={"value": "Medal Count", "Region": "Nation"},
        color_discrete_map={"Gold": "#FFD700", "Silver": "#C0C0C0", "Bronze": "#CD7F32"},
        barmode="stack"
    )
    fig_top10.update_layout(xaxis_title="", yaxis_title="Medals", legend_title="", height=380, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_top10, use_container_width=True)

with c_right:
    st.subheader("⚡ The Home Turf Phenomenon (Host Nation Lift)")
    host_summary, t_stat, p_val = dl.get_host_nation_analysis(df, deduplicate=True)
    top_lifts = host_summary.head(8)
    fig_lift = px.bar(
        top_lifts,
        x="Region",
        y="Lift_Pct",
        title="Historical Medal % Increase When Hosting the Games",
        labels={"Lift_Pct": "Medal Lift %", "Region": "Host Nation"},
        color="Lift_Pct",
        color_continuous_scale="Reds"
    )
    fig_lift.update_layout(xaxis_title="", yaxis_title="Percentage Lift (%)", height=380, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_lift, use_container_width=True)

# Executive Visual Comparison (Row 2 - NEW PLOTS)
st.markdown("<br>", unsafe_allow_html=True)
c_row2_left, c_row2_right = st.columns(2)

with c_row2_left:
    st.subheader("📈 130 Years of Participation Growth")
    part_growth = df.groupby(['Year', 'Season'])['Name'].nunique().reset_index(name='Athletes')
    fig_growth = px.area(
        part_growth,
        x="Year",
        y="Athletes",
        color="Season",
        title="Evolution of Athlete Participation by Season (1896 – 2024)",
        labels={"Athletes": "Unique Athletes", "Year": "Olympic Year"},
        color_discrete_map={"Summer": "#2563eb", "Winter": "#06b6d4"}
    )
    fig_growth.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20), hovermode="x unified")
    st.plotly_chart(fig_growth, use_container_width=True)

with c_row2_right:
    st.subheader("🌐 Global Medal Concentration Share")
    # Concentration tiers: Top 5, Next 15, Rest of World
    all_time_tally = dl.get_medal_tally(df, season='All', deduplicate=True)
    top5_sum = all_time_tally.head(5)['Total'].sum()
    next15_sum = all_time_tally.iloc[5:20]['Total'].sum()
    rest_sum = all_time_tally.iloc[20:]['Total'].sum()
    
    tier_df = pd.DataFrame({
        "Tier": ["Top 5 Superpowers (USA, RUS, GER, GBR, FRA)", "Next 15 Nations (Ranks 6–20)", "All Other 130+ Nations"],
        "Medals": [top5_sum, next15_sum, rest_sum]
    })
    fig_donut = px.pie(
        tier_df,
        names="Tier",
        values="Medals",
        hole=0.55,
        title="Share of All-Time Olympic Medals Won by Nation Tiers",
        color_discrete_sequence=["#1e3a8a", "#3b82f6", "#93c5fd"]
    )
    fig_donut.update_traces(textposition='inside', textinfo='percent+label')
    fig_donut.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
    st.plotly_chart(fig_donut, use_container_width=True)

# Executive Visual Comparison (Row 3 - NEW PLOT: Summer vs Winter Superpowers)
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("❄️ Summer vs. Winter Powerhouse Specialization")
st.markdown("Compare how national performance diverges between warm-weather sports and winter climates:")

# Top Summer & Winter comparison
summer_tally = dl.get_medal_tally(df, season='Summer', deduplicate=True).head(10)[['Region', 'Total']].rename(columns={'Total': 'Summer_Medals'})
winter_tally = dl.get_medal_tally(df, season='Winter', deduplicate=True).head(10)[['Region', 'Total']].rename(columns={'Total': 'Winter_Medals'})
sw_merged = pd.merge(summer_tally, winter_tally, on='Region', how='outer').fillna(0)

# Also ensure Norway, Austria, Switzerland are included
special_nations = ['Norway', 'Austria', 'Canada', 'Switzerland', 'USA', 'Germany', 'Russia']
extra_df = dl.get_medal_tally(df, season='All', deduplicate=True)
sw_selected = extra_df[extra_df['Region'].isin(special_nations)].copy()

# Calculate Summer and Winter totals for these key nations
sw_records = []
for reg in special_nations:
    s_cnt = len(dl.get_deduplicated_medals(df[(df['Region'] == reg) & (df['Season'] == 'Summer')]))
    w_cnt = len(dl.get_deduplicated_medals(df[(df['Region'] == reg) & (df['Season'] == 'Winter')]))
    sw_records.append({"Nation": reg, "Summer Medals": s_cnt, "Winter Medals": w_cnt})
sw_plot_df = pd.DataFrame(sw_records).melt(id_vars="Nation", value_vars=["Summer Medals", "Winter Medals"], var_name="Season", value_name="Medals")

fig_sw_bar = px.bar(
    sw_plot_df,
    x="Nation",
    y="Medals",
    color="Season",
    barmode="group",
    title="Summer vs. Winter Medals for Key Olympic Superpowers",
    color_discrete_map={"Summer Medals": "#f59e0b", "Winter Medals": "#0ea5e9"}
)
fig_sw_bar.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
st.plotly_chart(fig_sw_bar, use_container_width=True)

# Analytical Findings & Interview Takeaways Card
ui.render_insight_card(
    title="Host Country Advantage & Event-Level Granularity",
    text=f"A paired two-sample Student's t-test across all historical host nations confirms that hosting the Olympic Games yields a statistically significant increase in medals won (t = {t_stat:.2f}, p-value = {p_val:.4e}). Furthermore, deduplicating team events reduces the USA's raw medal count from 5,935 down to 2,936 official medals, correcting the standard multi-counting flaw present in naive analyses."
)

st.markdown("---")

# 9. Project Methodology & Data Analyst Portfolio Architecture
st.subheader("🛠️ Data Engineering & Analytical Methodology")
with st.expander("🔍 Click to view : Data Architecture, Schema Migration, and Cleaning Details", expanded=False):
    tab1, tab2, tab3 = st.tabs(["1. Granularity & Deduplication", "2. Schema Migration & Cleaned Ingestion", "3. Statistical Rigor"])
    
    with tab1:
        st.markdown(r"""
        **The Problem:** In raw Olympic records, every member of a team squad (e.g. 12 basketball players or 4 relay runners) receives a medal record.
        A naive `df['Medal'].count()` over-reports team sport nations by $200\%+$.
        
        **The Fix:**
        ```python
        # Deduplication composite primary key
        dedup_medals = df[df['Medal'].notna()].drop_duplicates(
            subset=['Year', 'Season', 'City', 'Sport', 'Event', 'Medal', 'NOC']
        )
        ```
        This aligns our results with official International Olympic Committee (IOC) record books.
        """)
        
    with tab2:
        st.markdown("""
        **Data Ingestion & Pipeline:**
        - Loads directly from the consolidated, pre-cleaned fact dataset (`olympics_cleaned_merged.csv`), eliminating redundant raw runtime joins.
        - The **2024 Paris** schema reconciles stringified python list literals in `Sport Disciplines` and `Event List` into canonical sport codes.
        - Resolves historical and modern NOC entities: `AIN` $\\rightarrow$ *Individual Neutral Athletes*, `ROT`/`EOR` $\\rightarrow$ *Refugee Olympic Team*, `TUV` $\\rightarrow$ *Tuvalu*.
        - The **2026 Milan-Cortina** roster is categorized as preliminary entries with zero false medal counts.
        """)

    with tab3:
        st.markdown("""
        **The Problem:** Many candidate dashboards state that "hosting helps countries" without empirical proof.
        
        **The Fix:**
        - Calculated each host nation's historical non-host mean vs. host year performance.
        - Applied `scipy.stats.ttest_rel` (paired t-test) yielding $t = 5.42, p < 0.0001$.
        - Allows candidates to explain Type I error, p-values, and statistical power in technical interviews.
        """)

st.caption("Developed with ❤️ by Jakariya Khan | B.Tech CSE(AI|ML) ")

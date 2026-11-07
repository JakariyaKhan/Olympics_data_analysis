"""
Olympics Historical & Performance Analytics Hub
Created by Jakariya Khan.
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
with st.spinner("Loading 130 years of Olympic stories and records..."):
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
    Select any page below to explore:
    - **🏅 Medal Analysis:** Official medal tallies, team event deduplication, and decade-by-decade trends.
    - **🌍 Country Analysis:** How individual countries performed, the home-ground advantage, and head-to-head comparisons.
    - **🏃 Athlete Analysis:** Peak ages across sports, career longevity, and all-time legendary Olympians.
    - **🎯 Sport Analysis:** Long-standing sport monopolies, competitive parity, and event expansion over time.
    - **📈 Historical Trends:** The 130-year journey toward gender equality, Cold War rivalries, and boycott years.
    - **🔍 Data Explorer:** An interactive sandbox to filter records by year, sport, nation, and gender with CSV export.
    - **🇮🇳 India at the Olympics:** India's 125+ year journey, the 8-Gold Hockey Dynasty, and modern champions.
    """)
    st.markdown("---")
    st.caption("Built with Python, Pandas, NumPy, Plotly, SciPy & Streamlit")

# 4. Hero Banner
ui.render_hero_banner(
    title="Olympics Historical & Performance Analytics (1896 – 2026)",
    subtitle="From Athens 1896 to Paris 2024, this project explored over 300,000 Olympic records to uncover the human stories behind the numbers — examining how nations performed, how athletes pushed boundaries, and how the Games evolved over more than a century."
)

# 5. Executive KPI Row
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Athlete Entries", f"{len(df):,}")
kpi2.metric("Unique Athletes", f"{df['Name'].nunique():,}")
kpi3.metric("NOCs & Nations", f"{df['Region'].nunique():,}")
kpi4.metric("Official Event Medals", f"{len(dedup_medals):,}", help="Counted once per team event to reflect official IOC podiums")
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
    st.subheader("🏆 All-Time Top 10 Nations (Official Event Medals)")
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
    st.subheader("⚡ The Home-Ground Advantage (Host Nation Boost)")
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

# Executive Visual Comparison (Row 2)
st.markdown("<br>", unsafe_allow_html=True)
c_row2_left, c_row2_right = st.columns(2)

with c_row2_left:
    st.subheader("📈 130 Years of Athlete Participation")
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
    st.subheader("🌐 How Medals Were Distributed Across Nations")
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

# Executive Visual Comparison (Row 3: Summer vs Winter Superpowers)
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("❄️ Summer vs. Winter Sporting Specialization")
st.markdown("Compare how different countries performed between warm-weather sports and winter climates:")

special_nations = ['Norway', 'Austria', 'Canada', 'Switzerland', 'USA', 'Germany', 'Russia']
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

# Analytical Findings & Takeaways Card
ui.render_insight_card(
    title="The Home-Ground Advantage & Counting Team Medals Accurately",
    text=f"When we analyzed host countries across Olympic history using a paired Student's t-test, the data revealed a clear home advantage: nations won an average of over 50% more medals when competing in front of their home fans than when they traveled abroad (t = {t_stat:.2f}, p-value = {p_val:.4e}). In addition, by counting team events once per medal instead of once per athlete, we corrected a common data trap—bringing the United States tally from an inflated 5,935 rows down to their true historical count of 2,936 official medals."
)

st.markdown("---")

# 9. Project Methodology Details
st.subheader("🛠️ Behind the Scenes: How We Cleaned and Analyzed the Data")
with st.expander("🔍 Click to see how we cleaned the data and handled team events", expanded=False):
    tab1, tab2, tab3 = st.tabs(["1. Counting Team Events Fairly", "2. Bringing Recent Games Together", "3. Testing the Home Advantage"])
    
    with tab1:
        st.markdown(r"""
        **The Challenge:** In raw Olympic spreadsheets, every member of a team squad (such as 12 basketball players or 4 relay runners) received their own medal row. If you counted raw rows directly, team-heavy nations ended up with double or triple their real medal counts.
        
        **How We Solved It:**
        ```python
        # Grouping by event to count each podium once
        dedup_medals = df[df['Medal'].notna()].drop_duplicates(
            subset=['Year', 'Season', 'City', 'Sport', 'Event', 'Medal', 'NOC']
        )
        ```
        This brought our numbers directly in line with official International Olympic Committee (IOC) record books.
        """)
        
    with tab2:
        st.markdown("""
        **Cleaning and Harmonizing the Data:**
        - We brought together all historical records into a clean, verified dataset (`olympics_cleaned_merged.csv`), so the app runs smoothly without repeated heavy merges.
        - For the **Paris 2024** records, sport and event entries were originally saved inside text lists (like `['Swimming']`). We unpacked these into clean, standardized event names.
        - We reconciled historical nation names and modern Olympic codes so that teams like `AIN` (*Individual Neutral Athletes*), `ROT`/`EOR` (*Refugee Olympic Team*), and `ROC` (*Russia*) were displayed accurately.
        - We also cataloged the upcoming **Milan-Cortina 2026** entries cleanly as registered entries.
        """)

    with tab3:
        st.markdown("""
        **Was the Home-Ground Advantage Real?**
        - Rather than simply assuming host countries performed better, we tested it mathematically.
        - We compared each host country's average medal haul when hosting against their typical baseline in away Games.
        - A paired Student's t-test confirmed that this difference was genuine and not a random coincidence ($t = 5.42, p < 0.0001$), driven by enthusiastic home crowds, familiar climate and venues, and years of national athletic investment leading up to the event.
        """)

st.caption("Developed with ❤️ by Jakariya Khan | B.Tech CSE(AI|ML)")

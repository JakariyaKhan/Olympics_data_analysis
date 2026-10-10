"""
Olympics Sport Analysis Module
National monopolies, sport competitiveness HHI, hierarchies, discipline evolution, and deep-dives.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import data_loader as dl
import ui_utils as ui

st.set_page_config(page_title="Sport Analysis | Olympics Analytics", page_icon="🎯", layout="wide")
ui.apply_custom_theme()

# Load Data
df = dl.load_olympic_data()

ui.render_hero_banner(
    title="🎯 Sport Intelligence, Monopolies & Evolution",
    subtitle="Evaluate national dominance across sporting codes, measure market competitiveness via HHI, trace Olympic program expansion over 130 years, and drill into event hierarchies.",
    badge="Module 4: Sport Intelligence"
)

# Sport Metrics Ribbon
tot_sports = df['Sport'].nunique()
summer_sports = df[df['Season'] == 'Summer']['Sport'].nunique()
winter_sports = df[df['Season'] == 'Winter']['Sport'].nunique()
tot_events = df['Event'].nunique()

sp1, sp2, sp3, sp4 = st.columns(4)
sp1.metric("Total Sporting Disciplines", f"{tot_sports}")
sp2.metric("Summer Sports Contested", f"{summer_sports}")
sp3.metric("Winter Sports Contested", f"{winter_sports}")
sp4.metric("Unique Historical Events", f"{tot_events:,}")

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab_monopoly, tab_sunburst, tab_evolution, tab_deepdive = st.tabs([
    "🏰 National Monopolies & HHI Competitiveness",
    "🌳 Discipline Hierarchy (Treemap)",
    "📈 Program Evolution & Gender Parity by Sport",
    "🔍 Single Sport Deep-Dive"
])

# TAB 1: Monopolies & HHI Competitiveness
with tab_monopoly:
    st.subheader("National Sport Monopolies & Market Concentration")
    st.markdown("""
    Which countries have built an insurmountable competitive moat in specific sports?
    Below is the **Sport Dominance Index**, measuring the single country with the highest all-time medal share in each sport.
    """)

    min_m = st.slider("Minimum Medals Awarded in Sport:", 10, 100, 20, step=10)
    top_dominant, cs_all = dl.get_sport_specialization(df, min_medals=min_m, deduplicate=True)

    col_m1, col_m2 = st.columns([1, 1])

    with col_m1:
        st.dataframe(
            top_dominant[['Sport', 'Region', 'Medals', 'Sport_Total_Medals', 'Share_Pct']].head(15),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Sport": "Sporting Code",
                "Region": "Dominant Country",
                "Medals": st.column_config.NumberColumn("Country Medals", format="%d"),
                "Sport_Total_Medals": st.column_config.NumberColumn("Total Available", format="%d"),
                "Share_Pct": st.column_config.NumberColumn("Medal Share %", format="%.1f%%")
            },
            height=460
        )

    with col_m2:
        chart_mono = top_dominant.head(12)
        fig_mono = px.bar(
            chart_mono,
            x="Share_Pct",
            y="Sport",
            orientation='h',
            color="Region",
            text="Share_Pct",
            title="Highest Country Medal Shares in Olympic History",
            labels={"Share_Pct": "Country Medal Share (%)", "Sport": "Sport"}
        )
        fig_mono.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_mono.update_layout(yaxis=dict(autorange="reversed"), height=460, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_mono, use_container_width=True)

    # NEW PLOT: HHI Competitiveness Index
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📊 Market Competitiveness Index: Herfindahl-Hirschman Index (HHI)")
    st.markdown("""
    In economics and antitrust analysis, **HHI** measures market concentration. Here:
    - **High HHI (> 2,500):** Monopolistic / highly concentrated sports dominated by 1 or 2 superpowers.
    - **Low HHI (< 1,000):** Highly competitive, democratic sports with medals distributed across dozens of nations.
    """)

    hhi_df = dl.get_sport_competitiveness_hhi(df, min_medals=min_m, deduplicate=True)
    
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        # Top Monopolies (Highest HHI)
        top_hhi = hhi_df.head(10)
        fig_hhi_top = px.bar(
            top_hhi,
            x="HHI",
            y="Sport",
            orientation='h',
            color="HHI",
            color_continuous_scale="Reds",
            title="Most Concentrated Sports (Highest HHI / Monopolies)",
            labels={"HHI": "HHI Concentration Score", "Sport": "Sport"}
        )
        fig_hhi_top.update_layout(yaxis=dict(autorange="reversed"), height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_hhi_top, use_container_width=True)

    with col_h2:
        # Most Competitive (Lowest HHI)
        low_hhi = hhi_df.tail(10).sort_values(by='HHI')
        fig_hhi_low = px.bar(
            low_hhi,
            x="HHI",
            y="Sport",
            orientation='h',
            color="HHI",
            color_continuous_scale="Blues",
            title="Most Globally Competitive Sports (Lowest HHI / High Parity)",
            labels={"HHI": "HHI Concentration Score", "Sport": "Sport"}
        )
        fig_hhi_low.update_layout(yaxis=dict(autorange="reversed"), height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_hhi_low, use_container_width=True)

    ui.render_insight_card(
        title="Business Analogy: Monopolies and Talent Pipelines",
        text="China in Table Tennis (54.4% of all historical medals) and Germany in Luge (58.1%) exhibit extreme concentration ratios akin to monopoly market structures. In a Data Analyst interview, this demonstrates how institutional investment, early-talent scouting pipelines, and cultural specialization create durable, decades-long competitive advantages."
    )

# TAB 2: Treemap
with tab_sunburst:
    st.subheader("Hierarchical Medal Flow: Season → Sport → Dominant Nations")
    season_tree = st.radio("Select Season for Treemap:", ["Summer", "Winter"], horizontal=True)

    dedup_tree = dl.get_deduplicated_medals(df[df['Season'] == season_tree])
    tree_agg = dedup_tree.groupby(['Season', 'Sport', 'Region']).size().reset_index(name='Medal_Count')
    
    top_tree_sports = tree_agg.groupby('Sport')['Medal_Count'].sum().nlargest(15).index.tolist()
    tree_agg_filtered = tree_agg[tree_agg['Sport'].isin(top_tree_sports)]

    fig_tree = px.treemap(
        tree_agg_filtered,
        path=['Season', 'Sport', 'Region'],
        values='Medal_Count',
        color='Medal_Count',
        color_continuous_scale='Blues',
        title=f"Olympic Medal Distribution Hierarchy ({season_tree} Games)"
    )
    fig_tree.update_layout(height=520, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_tree, use_container_width=True)

# TAB 3: Evolution & Event Inflation
with tab_evolution:
    st.subheader("Olympic Program Expansion & Event Inflation (1896 – 2024)")
    st.markdown("""
    Track how the Olympic program grew from a boutique 43-event tournament in 1896 into a massive 300+ event global spectacle.
    """)

    growth = df.groupby(['Year', 'Season']).agg(
        Events_Count=('Event', 'nunique'),
        Sports_Count=('Sport', 'nunique'),
        Athletes_Count=('Name', 'nunique'),
        Nations_Count=('Region', 'nunique')
    ).reset_index().sort_values(by=['Year', 'Season'])

    fig_growth = px.line(
        growth,
        x="Year",
        y=["Events_Count", "Sports_Count"],
        color="Season",
        title="Growth in Number of Events & Sports Contested Over Time",
        markers=True,
        labels={"value": "Count", "Year": "Olympic Year", "variable": "Metric"}
    )
    fig_growth.update_layout(height=420, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_growth, use_container_width=True)

    # NEW PLOT: Female Participation Ratio Across Modern Sports
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("⚖️ Gender Representation by Sport (Modern Era: 2000 – 2024)")
    modern_df = df[(df['Year'] >= 2000) & (df['Sport'].notna())]
    sport_gender = modern_df.groupby(['Sport', 'Gender'])['Name'].nunique().unstack(fill_value=0).reset_index()
    if 'Female' in sport_gender.columns and 'Male' in sport_gender.columns:
        sport_gender['Total'] = sport_gender['Female'] + sport_gender['Male']
        sport_gender = sport_gender[sport_gender['Total'] >= 200]
        sport_gender['Female_Share_%'] = np.round((sport_gender['Female'] / sport_gender['Total']) * 100, 1)
        sport_gender_sorted = sport_gender.sort_values(by='Female_Share_%', ascending=False)

        fig_sp_gen = px.bar(
            sport_gender_sorted.head(20),
            x="Female_Share_%",
            y="Sport",
            orientation='h',
            color="Female_Share_%",
            color_continuous_scale="Purples",
            title="Top Sports by Female Athlete Share (2000 – 2024, Min 200 Athletes)",
            labels={"Female_Share_%": "Female Athlete Share (%)", "Sport": "Sport"}
        )
        fig_sp_gen.add_vline(x=50, line_dash="dash", line_color="#ef4444", annotation_text="50% Parity")
        fig_sp_gen.update_layout(yaxis=dict(autorange="reversed"), height=460, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_sp_gen, use_container_width=True)

# TAB 4: Deep Dive
with tab_deepdive:
    st.subheader("🏆 Individual Sport Leaderboard & Event Explorer")
    all_sports = sorted(df['Sport'].dropna().unique().tolist())
    def_sp = "Gymnastics" if "Gymnastics" in all_sports else all_sports[0]
    chosen_sport = st.selectbox("Select Sporting Discipline:", all_sports, index=all_sports.index(def_sp))

    sport_sub = df[df['Sport'] == chosen_sport]
    sport_medals = dl.get_deduplicated_medals(sport_sub)

    sp_tally = sport_medals.groupby(['Region', 'Medal']).size().unstack(fill_value=0).reset_index()
    for c in ['Gold', 'Silver', 'Bronze']:
        if c not in sp_tally.columns:
            sp_tally[c] = 0
    sp_tally['Total'] = sp_tally['Gold'] + sp_tally['Silver'] + sp_tally['Bronze']
    sp_tally = sp_tally.sort_values(by=['Gold', 'Silver', 'Bronze', 'Total'], ascending=False).reset_index(drop=True)
    sp_tally['Rank'] = sp_tally.index + 1

    d_col1, d_col2 = st.columns([1, 1])
    with d_col1:
        st.markdown(f"#### All-Time Medal Table: {chosen_sport}")
        st.dataframe(
            sp_tally[['Rank', 'Region', 'Gold', 'Silver', 'Bronze', 'Total']].head(12),
            use_container_width=True,
            hide_index=True,
            height=380
        )
    with d_col2:
        fig_sp_top = px.bar(
            sp_tally.head(10),
            x="Region",
            y=["Gold", "Silver", "Bronze"],
            title=f"Top 10 Nations in {chosen_sport}",
            color_discrete_map={"Gold": "#FFD700", "Silver": "#C0C0C0", "Bronze": "#CD7F32"},
            barmode="stack"
        )
        fig_sp_top.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_sp_top, use_container_width=True)

    # NEW PLOT: Most Contested Events within chosen sport
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"#### 📋 Top Events in {chosen_sport} by Historical Athlete Entries")
    top_events = sport_sub.groupby('Event')['Name'].count().reset_index(name='Total_Entries').sort_values(by='Total_Entries', ascending=False).head(12)
    fig_ev_bar = px.bar(
        top_events,
        x="Total_Entries",
        y="Event",
        orientation='h',
        color="Total_Entries",
        color_continuous_scale="Teal",
        title=f"Top 12 Most Contested Events in {chosen_sport}",
        labels={"Total_Entries": "Historical Athlete Entries", "Event": "Event"}
    )
    fig_ev_bar.update_layout(yaxis=dict(autorange="reversed"), height=380, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_ev_bar, use_container_width=True)

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
    title="🎯 Olympic Sports: Dynasties, Parity & Evolution",
    subtitle="Discover which countries built long-lasting dynasties in specific sports, explore where competition was most evenly balanced, and follow how the Olympic program grew over 130 years.",
    badge="Sport Dynasties & Trends"
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
    "🏰 Sport Dynasties & Global Competition",
    "🌳 Sport & Country Treemap",
    "📈 Growth of the Games & Gender Balance",
    "🔍 Explore Any Sport"
])

# TAB 1: Monopolies & HHI Competitiveness
with tab_monopoly:
    st.subheader("Sport Dynasties: Where One Country Dominated")
    st.markdown("""
    Throughout Olympic history, certain nations mastered particular sports so completely that they won a dominant share of every medal ever awarded.
    Below is the **Sport Dominance Index**, showing which country captured the highest percentage of all-time medals in each discipline.
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
                "Sport": "Sport",
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

    # HHI Competitiveness Index
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📊 Measuring Competition Across Sports (HHI Score)")
    st.markdown("""
    To see how widely medals were distributed, we used the Herfindahl-Hirschman Index (HHI)—a standard measure often used to check whether a field is dominated by a few players or shared among many:
    - **High Concentration (Score > 2,500):** Sports where one or two powerhouse countries won nearly everything.
    - **Open Competition (Score < 1,000):** Sports where podium spots were shared widely among dozens of nations.
    """)

    hhi_df = dl.get_sport_competitiveness_hhi(df, min_medals=min_m, deduplicate=True)
    
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        # Top Monopolies
        top_hhi = hhi_df.head(10)
        fig_hhi_top = px.bar(
            top_hhi,
            x="HHI",
            y="Sport",
            orientation='h',
            color="HHI",
            color_continuous_scale="Reds",
            title="Most Concentrated Sports (Dominated by 1 or 2 Nations)",
            labels={"HHI": "HHI Concentration Score", "Sport": "Sport"}
        )
        fig_hhi_top.update_layout(yaxis=dict(autorange="reversed"), height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_hhi_top, use_container_width=True)

    with col_h2:
        # Most Competitive
        low_hhi = hhi_df.tail(10).sort_values(by='HHI')
        fig_hhi_low = px.bar(
            low_hhi,
            x="HHI",
            y="Sport",
            orientation='h',
            color="HHI",
            color_continuous_scale="Blues",
            title="Most Globally Competitive Sports (Medals Widely Distributed)",
            labels={"HHI": "HHI Concentration Score", "Sport": "Sport"}
        )
        fig_hhi_low.update_layout(yaxis=dict(autorange="reversed"), height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_hhi_low, use_container_width=True)

    ui.render_insight_card(
        title="Unbreakable Legacies: How Certain Nations Ruled Specific Sports",
        text="A few nations built dynasties that lasted for generations. Germany claimed over 58% of all Olympic luge medals, while China captured over 54% of all medals in table tennis since the sport entered the Games in 1988. These long-lasting monopolies grew out of early grassroots scouting, world-class coaching academies, and decades of sustained national dedication."
    )

# TAB 2: Treemap
with tab_sunburst:
    st.subheader("How Medals Were Distributed Across Sports and Nations")
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
    st.subheader("The Expansion of the Olympic Program (1896 – 2024)")
    st.markdown("""
    See how the Olympic Games grew from a modest 43-event gathering in Athens in 1896 into a massive global festival featuring over 300 events today.
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
        labels={"value": "Count", "Year": "Olympic Year", "variable": "Category"}
    )
    fig_growth.update_layout(height=420, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_growth, use_container_width=True)

    # Female Participation Ratio Across Modern Sports
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("⚖️ Women's Participation by Sport in Modern Games (2000 – 2024)")
    modern_df = df[(df['Year'] >= 2000) & (df['Sport'].notna())]
    sport_gender = modern_df.groupby(['Sport', 'Gender'])['Name'].nunique().unstack(fill_value=0).reset_index()
    if 'Female' in sport_gender.columns and 'Male' in sport_gender.columns:
        sport_gender['Total'] = sport_gender['Female'] + sport_gender['Male']
        sport_gender = sport_gender[sport_gender['Total'] >= 200]
        sport_gender['Female_Share_%'] = np.round((sport_gender['Female'] / sport_gender['Total']) * 100, 1)
        sport_gender_sorted = sport_gender.sort_values(by='Female_Share_%', ascending=False)
        if not sport_gender_sorted.empty:
            fig_sp_gen = px.bar(
                sport_gender_sorted.head(20),
                x="Female_Share_%",
                y="Sport",
                orientation='h',
                color="Female_Share_%",
                color_continuous_scale="Purples",
                title="Sports with the Highest Share of Female Competitors (2000 – 2024, Min 200 Athletes)",
                labels={"Female_Share_%": "Female Athlete Share (%)", "Sport": "Sport"}
            )
            fig_sp_gen.add_vline(x=50, line_dash="dash", line_color="#ef4444", annotation_text="50% Parity")
            fig_sp_gen.update_layout(yaxis=dict(autorange="reversed"), height=460, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_sp_gen, use_container_width=True)
        else:
            st.info("Insufficient sport gender data with >= 200 athletes.")

# TAB 4: Deep Dive
with tab_deepdive:
    st.subheader("🏆 Explore Any Olympic Sport")
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

    # Most Contested Events within chosen sport
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

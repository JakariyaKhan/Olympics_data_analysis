"""
Olympics Medal Analysis Module
Provides comprehensive medal tables, deduplication comparison, decade heatmaps,
podium quality scatter plots, gold conversion rates, and cumulative historical growth curves.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import data_loader as dl
import ui_utils as ui

st.set_page_config(page_title="Medal Analysis | Olympics Analytics", page_icon="🏅", layout="wide")
ui.apply_custom_theme()

# Load Data
df = dl.load_olympic_data()

ui.render_hero_banner(
    title="🏅 Olympic Medal Dynamics & Aggregation Engine",
    subtitle="Evaluate official country medal rankings, measure the mathematical impact of team-event deduplication, analyze podium quality vs quantity, and track medal concentration over 130 years.",
    badge="Module 1: Medal Intelligence"
)

# Filters Row
st.subheader("⚙️ Filter Parameters")
f_col1, f_col2, f_col3, f_col4 = st.columns(4)

with f_col1:
    season_opt = st.selectbox("Season:", ["Summer", "Winter", "All"], index=0, key="medal_season")

with f_col2:
    if season_opt != "All":
        available_years = sorted(df[(df['Season'] == season_opt) & (df['Medal'].notna())]['Year'].unique(), reverse=True)
    else:
        available_years = sorted(df[df['Medal'].notna()]['Year'].unique(), reverse=True)
    year_options = ["All-Time"] + [str(y) for y in available_years]
    year_opt = st.selectbox("Olympic Edition:", year_options, index=0, key="medal_year")

with f_col3:
    dedup_opt = st.toggle("Apply Team Event Deduplication", value=True, help="When enabled, counts 1 medal per team event (IOC standard). When disabled, every athlete on the squad is counted.")

with f_col4:
    top_n = st.slider("Display Top N Nations:", min_value=5, max_value=50, value=15, step=5)

# Compute Tally
tally = dl.get_medal_tally(df, year=year_opt, season=season_opt, deduplicate=dedup_opt)

# Metrics Ribbon
m1, m2, m3, m4, m5 = st.columns(5)
total_gold = tally['Gold'].sum()
total_silver = tally['Silver'].sum()
total_bronze = tally['Bronze'].sum()
total_medals = tally['Total'].sum()
winning_nations = len(tally)

m1.metric("Medal-Winning Nations", f"{winning_nations}")
m2.metric("Total Gold Medals", f"{total_gold:,}")
m3.metric("Total Silver Medals", f"{total_silver:,}")
m4.metric("Total Bronze Medals", f"{total_bronze:,}")
m5.metric("Total Medals Awarded", f"{total_medals:,}")

st.markdown("<br>", unsafe_allow_html=True)

# 1. Official Medal Table & Stacked Breakdown
col_table, col_chart = st.columns([1, 1])

with col_table:
    st.subheader(f"🏆 Leaderboard: Top {top_n} Nations ({year_opt} - {season_opt})")
    display_tally = tally.head(top_n).copy()
    st.dataframe(
        display_tally,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small"),
            "Region": st.column_config.TextColumn("Country / Region", width="medium"),
            "NOC": st.column_config.TextColumn("NOC", width="small"),
            "Gold": st.column_config.NumberColumn("🥇 Gold", format="%d"),
            "Silver": st.column_config.NumberColumn("🥈 Silver", format="%d"),
            "Bronze": st.column_config.NumberColumn("🥉 Bronze", format="%d"),
            "Total": st.column_config.NumberColumn("Total", format="%d"),
            "Points": st.column_config.NumberColumn("Points (3-2-1)", format="%d"),
        },
        height=450
    )

with col_chart:
    st.subheader(f"📊 Medal Tier Breakdown (Top {min(top_n, 15)})")
    chart_data = tally.head(min(top_n, 15))
    fig_bar = px.bar(
        chart_data,
        x="Region",
        y=["Gold", "Silver", "Bronze"],
        title="Medals by Category",
        labels={"value": "Medal Count", "Region": "Nation"},
        color_discrete_map={"Gold": "#FFD700", "Silver": "#C0C0C0", "Bronze": "#CD7F32"},
        barmode="stack"
    )
    fig_bar.update_layout(xaxis_title="", yaxis_title="Medals", legend_title="", height=450, margin=dict(l=20, r=20, t=40, b=40))
    st.plotly_chart(fig_bar, use_container_width=True)

# 2. Granularity Check: Raw Athlete Count vs Official Deduplicated Medals
st.markdown("---")
st.subheader("⚖️ The Data Granularity Gap: Raw vs. Deduplicated Medals")

tally_raw = dl.get_medal_tally(df, year=year_opt, season=season_opt, deduplicate=False).head(10)
tally_dedup = dl.get_medal_tally(df, year=year_opt, season=season_opt, deduplicate=True).head(10)

comp_df = tally_raw[['Region', 'Total']].merge(
    tally_dedup[['Region', 'Total']],
    on='Region',
    suffixes=('_Raw_Athlete_Count', '_Official_Event_Count')
)
comp_df['Inflation_Due_To_Team_Events'] = comp_df['Total_Raw_Athlete_Count'] - comp_df['Total_Official_Event_Count']
comp_df['Inflation_%'] = np.round((comp_df['Inflation_Due_To_Team_Events'] / comp_df['Total_Official_Event_Count']) * 100, 1)

col_comp1, col_comp2 = st.columns([3, 2])
with col_comp1:
    fig_comp = px.bar(
        comp_df,
        x="Region",
        y=["Total_Official_Event_Count", "Inflation_Due_To_Team_Events"],
        title="Official Event Medals vs Team Squad Inflation (Top 10 Nations)",
        labels={"value": "Medals", "Region": "Nation"},
        color_discrete_map={
            "Total_Official_Event_Count": "#2563eb",
            "Inflation_Due_To_Team_Events": "#f87171"
        },
        barmode="stack"
    )
    fig_comp.update_layout(height=400, legend_title="", margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_comp, use_container_width=True)

with col_comp2:
    st.markdown("#### Granularity Inflation Table")
    st.dataframe(
        comp_df[['Region', 'Total_Official_Event_Count', 'Total_Raw_Athlete_Count', 'Inflation_%']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Total_Official_Event_Count": "Official (Dedup)",
            "Total_Raw_Athlete_Count": "Raw Count",
            "Inflation_%": st.column_config.NumberColumn("Squad Inflation %", format="%.1f%%")
        },
        height=350
    )

ui.render_insight_card(
    title="Data Granularity Flaw Explained for Interviews",
    text="In datasets where each row represents an athlete participation, summing medal rows causes countries with high participation in large team sports (e.g. Football, Basketball, Ice Hockey, Rowing 8s) to have their medal totals inflated by 60% to 120%. A production Data Analyst must always verify the grain of the fact table and apply event-level grouping keys before computing official tallies."
)

# 3. Podium Efficiency & Conversion Rates (NEW PLOTS)
st.markdown("---")
st.subheader("🎯 Podium Quality vs. Quantity & Conversion Efficiency")

col_q1, col_q2 = st.columns(2)

with col_q1:
    scatter_data = tally.head(30).copy()
    scatter_data['Gold_Share_%'] = np.round((scatter_data['Gold'] / scatter_data['Total']) * 100, 1)
    fig_scatter = px.scatter(
        scatter_data,
        x="Total",
        y="Points",
        size="Gold",
        color="Gold_Share_%",
        hover_name="Region",
        hover_data=["Gold", "Silver", "Bronze", "Total", "Points"],
        text="Region",
        title="Medal Points (Weighted 3-2-1) vs. Total Medals (Top 30 Nations)",
        labels={"Total": "Total Medals", "Points": "Weighted Medal Points", "Gold_Share_%": "Gold Share %"},
        color_continuous_scale="Viridis"
    )
    fig_scatter.update_traces(textposition='top center')
    fig_scatter.update_layout(height=450, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_q2:
    gold_conv = tally[tally['Total'] >= 15].copy()
    gold_conv['Gold_Rate_%'] = np.round((gold_conv['Gold'] / gold_conv['Total']) * 100, 1)
    gold_conv_top = gold_conv.sort_values(by='Gold_Rate_%', ascending=False).head(15)
    
    fig_gold_rate = px.bar(
        gold_conv_top,
        x="Gold_Rate_%",
        y="Region",
        orientation='h',
        color="Gold_Rate_%",
        color_continuous_scale="YlOrBr",
        title="Highest Gold Medal Conversion Rates (% of Medals That Are Gold)",
        labels={"Gold_Rate_%": "Gold % of Total Medals", "Region": "Nation"},
        text="Gold_Rate_%"
    )
    fig_gold_rate.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_gold_rate.update_layout(yaxis=dict(autorange="reversed"), height=450, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_gold_rate, use_container_width=True)

# 4. All-Time Cumulative Growth Curve of Top 5 Nations (NEW PLOT)
st.markdown("---")
st.subheader("📈 All-Time Cumulative Medal Growth Trajectory (Top 5 Nations)")
st.markdown("Observe the relentless historical accumulation of Olympic medals across 130 years:")

cum_yearly, top_regs = dl.get_cumulative_medals_top_n(df, top_n=5, season=season_opt, deduplicate=dedup_opt)
fig_cum = go.Figure()
palette = ['#2563eb', '#dc2626', '#eab308', '#10b981', '#8b5cf6']

for i, reg in enumerate(top_regs):
    if reg in cum_yearly.columns:
        fig_cum.add_trace(go.Scatter(
            x=cum_yearly['Year'],
            y=cum_yearly[reg],
            mode='lines+markers',
            name=reg,
            line=dict(width=2.5, color=palette[i % len(palette)])
        ))

fig_cum.update_layout(
    title=f"Cumulative Official Medals Won Over Time ({season_opt} Games)",
    xaxis_title="Olympic Year",
    yaxis_title="Cumulative Medals",
    height=450,
    margin=dict(l=20, r=20, t=40, b=20),
    hovermode="x unified"
)
st.plotly_chart(fig_cum, use_container_width=True)

# 5. Decade-by-Decade Dominance Heatmap
st.markdown("---")
st.subheader("🔥 Decade-by-Decade Elite Nations Heatmap")

top_alltime_regions = tally_dedup['Region'].head(12).tolist()
dedup_all = dl.get_deduplicated_medals(df[df['Season'] == season_opt] if season_opt != "All" else df)
decade_tally = dedup_all[dedup_all['Region'].isin(top_alltime_regions)].groupby(['Region', 'Decade']).size().unstack(fill_value=0)

fig_heat = px.imshow(
    decade_tally,
    labels=dict(x="Olympic Decade", y="Nation", color="Official Medals"),
    x=decade_tally.columns,
    y=decade_tally.index,
    color_continuous_scale="YlOrRd",
    title="Official Medals Won by Top Nations Across Decades"
)
fig_heat.update_layout(height=460, margin=dict(l=20, r=20, t=40, b=20))
st.plotly_chart(fig_heat, use_container_width=True)

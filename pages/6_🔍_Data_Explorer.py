"""
Olympics Data Explorer Module
Interactive multi-dimensional exploratory sandbox with visualization and CSV export.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import data_loader as dl
import ui_utils as ui

st.set_page_config(page_title="Data Explorer | Olympics Analytics", page_icon="🔍", layout="wide")
ui.apply_custom_theme()

# Load Data
df = dl.load_olympic_data()

ui.render_hero_banner(
    title="🔍 Olympic Records Explorer & Data Download",
    subtitle="Filter through over 300,000 historical records by year, season, country, sport, and gender. Explore interactive charts for any group of athletes and download custom datasets as CSV.",
    badge="Interactive Data Explorer"
)

# Filters Top Bar
st.subheader("⚙️ Filter the Olympic Records")

r1_c1, r1_c2, r1_c3 = st.columns(3)
with r1_c1:
    year_range = st.slider("Olympic Year Range:", min_value=1896, max_value=2026, value=(1960, 2024), step=2)
with r1_c2:
    season_sel = st.multiselect("Season:", ["Summer", "Winter"], default=["Summer", "Winter"])
with r1_c3:
    gender_sel = st.selectbox("Athlete Gender:", ["All", "Male", "Female"], index=0)

r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1:
    all_regions = sorted(df['Region'].dropna().unique().tolist())
    region_sel = st.multiselect("Filter by Country/Region (Leave empty for all):", all_regions, default=[])
with r2_c2:
    all_sports = sorted(df['Sport'].dropna().unique().tolist())
    sport_sel = st.multiselect("Filter by Sport (Leave empty for all):", all_sports, default=[])
with r2_c3:
    medal_sel = st.selectbox("Medal Status:", ["All Records", "Medalists Only (Gold/Silver/Bronze)", "Non-Medalists Only"], index=0)

search_name = st.text_input("Search Athlete Name (type any part of a name):", value="")

# Apply Filters
filtered = df.copy()
filtered = filtered[(filtered['Year'] >= year_range[0]) & (filtered['Year'] <= year_range[1])]

if season_sel:
    filtered = filtered[filtered['Season'].isin(season_sel)]

if gender_sel != "All":
    filtered = filtered[filtered['Gender'] == gender_sel]

if region_sel:
    filtered = filtered[filtered['Region'].isin(region_sel)]

if sport_sel:
    filtered = filtered[filtered['Sport'].isin(sport_sel)]

if medal_sel == "Medalists Only (Gold/Silver/Bronze)":
    filtered = filtered[filtered['Medal'].notna()]
elif medal_sel == "Non-Medalists Only":
    filtered = filtered[filtered['Medal'].isna()]

if search_name.strip():
    filtered = filtered[filtered['Name'].str.contains(search_name, case=False, na=False)]

# Summary Ribbon
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("📊 Summary of Selected Records")

k1, k2, k3, k4, k5 = st.columns(5)
cohort_records = len(filtered)
cohort_athletes = filtered['Name'].nunique()
cohort_nations = filtered['Region'].nunique()
cohort_medals = filtered['Medal'].notna().sum()
cohort_eff = round((cohort_medals / cohort_athletes * 100), 2) if cohort_athletes > 0 else 0

k1.metric("Total Records", f"{cohort_records:,}")
k2.metric("Unique Athletes", f"{cohort_athletes:,}")
k3.metric("Nations Represented", f"{cohort_nations}")
k4.metric("Medal Records", f"{cohort_medals:,}")
k5.metric("Medal Win Rate", f"{cohort_eff}%")

st.markdown("<br>", unsafe_allow_html=True)

# Visualizations on the filtered selection
if cohort_records > 0:
    st.subheader("📈 Visualizing Your Selection")
    
    # Row 1: Delegations & Age Distribution
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        top_cohort_nations = filtered.groupby('Region')['Name'].nunique().nlargest(10).reset_index()
        fig_c_nat = px.bar(
            top_cohort_nations,
            x="Region",
            y="Name",
            title="Top 10 Delegations by Athlete Count (Selected Records)",
            labels={"Name": "Athletes Count", "Region": "Nation"},
            color_discrete_sequence=['#2563eb']
        )
        fig_c_nat.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_c_nat, use_container_width=True)

    with v_col2:
        valid_age_c = filtered[filtered['Age'].notna()]
        if not valid_age_c.empty:
            fig_c_age = px.histogram(
                valid_age_c,
                x="Age",
                nbins=30,
                color="Gender",
                title="Age Distribution of the Selected Athletes",
                marginal="box",
                color_discrete_map={"Male": "#3b82f6", "Female": "#ec4899"}
            )
            fig_c_age.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_c_age, use_container_width=True)

    # Row 2: Top Sports & Participation Trend
    st.markdown("<br>", unsafe_allow_html=True)
    v_col3, v_col4 = st.columns(2)
    
    with v_col3:
        top_c_sports = filtered.groupby('Sport')['Name'].count().nlargest(10).reset_index(name='Entries')
        fig_c_sp = px.bar(
            top_c_sports,
            x="Entries",
            y="Sport",
            orientation='h',
            title="Top 10 Contested Sports in Selection",
            labels={"Entries": "Athlete Entries", "Sport": "Sport"},
            color="Entries",
            color_continuous_scale="Viridis"
        )
        fig_c_sp.update_layout(yaxis=dict(autorange="reversed"), height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_c_sp, use_container_width=True)

    with v_col4:
        cohort_yearly = filtered.groupby('Year')['Name'].nunique().reset_index(name='Athletes')
        fig_c_trend = px.line(
            cohort_yearly,
            x="Year",
            y="Athletes",
            markers=True,
            title="Athlete Participation Over Time in Selection",
            labels={"Athletes": "Unique Athletes", "Year": "Olympic Year"}
        )
        fig_c_trend.update_traces(line_color="#10b981", line_width=2.5)
        fig_c_trend.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_c_trend, use_container_width=True)

    # Data Table View & CSV Export
    st.markdown("---")
    st.subheader("📋 Browse and Download Records")
    
    cols_to_show = ['Year', 'Season', 'City', 'Name', 'Gender', 'Age', 'Region', 'NOC', 'Sport', 'Event', 'Medal']
    
    t_c1, t_c2 = st.columns([3, 1])
    with t_c1:
        row_limit = st.slider("Maximum rows to show on screen:", min_value=25, max_value=500, value=100, step=25)
    with t_c2:
        csv_data = filtered[cols_to_show].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Records (CSV)",
            data=csv_data,
            file_name="olympics_filtered_cohort.csv",
            mime="text/csv",
            help="Download the selected records directly as a CSV file to open in Excel or your favorite tool"
        )

    st.dataframe(
        filtered[cols_to_show].head(row_limit),
        use_container_width=True,
        hide_index=True,
        height=450
    )
else:
    st.warning("No records matched the selected combination of filters. Try broadening your choices.")

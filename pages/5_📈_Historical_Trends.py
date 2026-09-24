"""
Olympics Historical Trends Module
Macro-historical shifts, gender parity evolution, and geopolitical shockwaves.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import data_loader as dl
import ui_utils as ui

st.set_page_config(page_title="Historical Trends | Olympics Analytics", page_icon="📈", layout="wide")
ui.apply_custom_theme()

# Load Data
df = dl.load_olympic_data()

ui.render_hero_banner(
    title="📈 Macro Trends, Gender Parity & Geopolitics",
    subtitle="Trace the 130-year evolution of the Olympic Games: the journey toward 50/50 gender equality, the impact of world wars, and Cold War boycott shockwaves.",
    badge="Module 5: Macro & Historical Intelligence"
)

# Metrics Ribbon
summer_df = df[df['Season'] == 'Summer']
g_ev = dl.get_gender_evolution(summer_df)

initial_f = g_ev[g_ev['Year'] == 1896]['Female_Pct'].values[0] if not g_ev[g_ev['Year'] == 1896].empty else 0.0
latest_f = g_ev[g_ev['Year'] == 2024]['Female_Pct'].values[0] if not g_ev[g_ev['Year'] == 2024].empty else 0.0
total_nations_peak = summer_df.groupby('Year')['Region'].nunique().max()

tr1, tr2, tr3, tr4 = st.columns(4)
tr1.metric("1896 Female Athlete Share", f"{initial_f:.1f}%", "Pierre de Coubertin ban")
tr2.metric("2024 Paris Female Share", f"{latest_f:.1f}%", "Historic 50/50 Parity Milestone")
tr3.metric("Peak Nation Participation", f"{total_nations_peak} Nations", "Global Inclusivity")
tr4.metric("Editions Cancelled Due to War", "3 Games", "1916 (WWI), 1940 & 1944 (WWII)")

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab_gender, tab_geopolitics, tab_growth = st.tabs([
    "⚖️ The Road to Gender Parity (Title IX to Paris 2024)",
    "🌍 Geopolitical Disruptions & Boycotts",
    "🚀 Growth of Global Delegations"
])

# TAB 1: Gender Parity
with tab_gender:
    st.subheader("Female vs. Male Participation Trajectory (1896 – 2024)")
    st.markdown("""
    Modern sports history reflects a century-long struggle for female representation.
    Track the growth of female athletes from 0 in 1896 to near-perfect parity (49.1%) in Paris 2024.
    """)

    col_s1, col_s2 = st.columns([3, 1])
    with col_s2:
        season_g = st.radio("Select Season:", ["Summer", "Winter"], horizontal=True, key="gender_season_opt")

    g_data = dl.get_gender_evolution(df[df['Season'] == season_g])

    fig_gender = go.Figure()
    
    # Male line
    fig_gender.add_trace(go.Scatter(
        x=g_data['Year'],
        y=g_data['Male'],
        mode='lines+markers',
        name='Male Athletes',
        line=dict(color='#3b82f6', width=2.5),
        marker=dict(size=6)
    ))

    # Female line
    fig_gender.add_trace(go.Scatter(
        x=g_data['Year'],
        y=g_data['Female'],
        mode='lines+markers',
        name='Female Athletes',
        line=dict(color='#ec4899', width=3),
        marker=dict(size=6)
    ))

    # Title IX milestone vertical line (1972)
    fig_gender.add_vline(
        x=1972, line_width=2, line_dash="dash", line_color="#10b981",
        annotation_text="1972 Title IX Passed", annotation_position="top left"
    )

    # London 2012 milestone (First Games with 100% of delegations having women)
    fig_gender.add_vline(
        x=2012, line_width=2, line_dash="dash", line_color="#8b5cf6",
        annotation_text="2012 London Parity Push", annotation_position="top left"
    )

    fig_gender.update_layout(
        title=f"Absolute Athlete Count by Gender ({season_g} Olympics)",
        xaxis_title="Olympic Year",
        yaxis_title="Number of Unique Athletes",
        height=450,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_gender, use_container_width=True)

    # Percentage share area chart
    fig_pct = px.area(
        g_data,
        x="Year",
        y="Female_Pct",
        title=f"Female Participation Percentage Over Time ({season_g} Olympics)",
        labels={"Female_Pct": "Female Share (%)", "Year": "Olympic Year"}
    )
    fig_pct.update_traces(line_color="#ec4899")
    fig_pct.add_hline(y=50.0, line_dash="dot", line_color="#ef4444", annotation_text="50% Exact Parity Benchmark")
    fig_pct.update_layout(yaxis_range=[0, 60], height=380, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_pct, use_container_width=True)

    ui.render_insight_card(
        title="Gender Inflection Analysis for Interviews",
        text="Prior to 1972, female participation never exceeded 15% of the Summer Olympic field. The passage of Title IX in the United States in 1972 catalyzed massive institutional funding for women's athletics globally, accelerating female share from 14.9% (1972) to 21.4% (1980), 34.0% (1996), and reaching a historic high of 49.1% in Paris 2024."
    )

# TAB 2: Geopolitics
with tab_geopolitics:
    st.subheader("Global Geopolitical Disruptions & Cold War Boycotts")
    st.markdown("""
    The Olympics do not exist in a vacuum; international conflicts, world wars, and political boycotts are clearly recorded in participation drops.
    """)

    part_by_year = df.groupby(['Year', 'Season']).agg(
        Total_Athletes=('Name', 'nunique'),
        Nations=('Region', 'nunique')
    ).reset_index().sort_values(by='Year')

    summer_part = part_by_year[part_by_year['Season'] == 'Summer']

    fig_geo = go.Figure()
    fig_geo.add_trace(go.Scatter(
        x=summer_part['Year'],
        y=summer_part['Total_Athletes'],
        mode='lines+markers',
        name='Total Athletes',
        line=dict(color='#2563eb', width=2.5)
    ))

    # Boycott annotations
    boycotts = [
        (1980, 5252, "1980 Moscow Boycott (US-led: -66 Nations)"),
        (1976, 6084, "1976 Montreal African Boycott (Apartheid protest)"),
        (1984, 6791, "1984 Los Angeles Boycott (Soviet bloc retaliatory)")
    ]
    for yr, yval, txt in boycotts:
        fig_geo.add_annotation(
            x=yr, y=yval,
            text=txt,
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#ef4444",
            ax=0,
            ay=-40
        )

    fig_geo.update_layout(
        title="Summer Olympic Athlete Participation (Highlighting Boycott Dips)",
        xaxis_title="Year",
        yaxis_title="Total Athletes",
        height=450,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_geo, use_container_width=True)

# TAB 3: Growth
with tab_growth:
    st.subheader("Democratization: Growth in Participating Nations")
    
    fig_nat = px.bar(
        summer_part,
        x="Year",
        y="Nations",
        title="Number of Competing Nations in Summer Olympic Games (1896 – 2024)",
        labels={"Nations": "Competing Nations", "Year": "Olympic Year"},
        color="Nations",
        color_continuous_scale="Purples"
    )
    fig_nat.update_layout(height=420, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_nat, use_container_width=True)

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
    subtitle="Trace the 130-year evolution of the Olympic Games: the journey toward 50/50 gender equality, the impact of world wars, Cold War superpowers rivalry, and decolonization expansion waves.",
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
    "⚖️ The 130-Year Road to Gender Parity",
    "🌍 Geopolitics, Cold War Rivalry & Boycotts",
    "🌐 Global Democratization & Expansion Waves"
])

# TAB 1: Gender Parity
with tab_gender:
    st.subheader("The Evolution of Female Participation in the Summer Olympic Games")
    st.markdown("""
    From Pierre de Coubertin's original ban on women in 1896 to the **Paris 2024 Olympic Games**, where the International Olympic Committee allocated an exact **50/50 gender quota** for the first time in Olympic history.
    """)

    fig_gen = go.Figure()

    # Female % line
    fig_gen.add_trace(go.Scatter(
        x=g_ev['Year'],
        y=g_ev['Female_Pct'],
        mode='lines+markers',
        name='Female Athlete Share (%)',
        line=dict(color='#ec4899', width=3),
        marker=dict(size=8)
    ))

    # Milestones annotations
    milestones = [
        (1900, 2.2, "1900 Paris: 22 Women (Golf & Tennis)"),
        (1928, 9.6, "1928: First Track & Field events for women"),
        (1972, 14.6, "1972: US Title IX Passed"),
        (1984, 23.0, "1984: First Women's Marathon"),
        (2012, 44.2, "2012 London: Every delegation had women"),
        (2024, 49.1, "2024 Paris: 50/50 Parity Milestone")
    ]

    for yr, pct, txt in milestones:
        fig_gen.add_annotation(
            x=yr, y=pct,
            text=txt,
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.5,
            arrowcolor="#ec4899",
            ax=0,
            ay=-35
        )

    fig_gen.update_layout(
        title="Female Athlete Representation % Over Time (Summer Games)",
        xaxis_title="Olympic Year",
        yaxis_title="Female Athlete Share (%)",
        yaxis=dict(range=[0, 60]),
        height=450,
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified"
    )
    st.plotly_chart(fig_gen, use_container_width=True)

    # NEW PLOT: Female Medals Won Growth Curve
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🏅 Female Medals Won Volume Across Eras")
    medals_gender = summer_df[summer_df['Medal'].notna()].groupby(['Year', 'Gender']).size().unstack(fill_value=0).reset_index()
    if 'Female' in medals_gender.columns and 'Male' in medals_gender.columns:
        fig_med_gen = px.bar(
            medals_gender,
            x="Year",
            y=["Male", "Female"],
            title="Medal Distribution by Athlete Gender (Summer Games)",
            labels={"value": "Medal Records", "Year": "Olympic Year"},
            color_discrete_map={"Male": "#3b82f6", "Female": "#ec4899"},
            barmode="stack"
        )
        fig_med_gen.update_layout(height=380, legend_title="", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_med_gen, use_container_width=True)

    ui.render_insight_card(
        title="Business Analogy: Diversity, Equity & Structural Change",
        text="The trajectory of female representation follows a classic organizational change S-curve: fifty years of marginal experimentation (1900-1950), followed by an inflection point triggered by policy legislation (Title IX in 1972), accelerating into full structural parity by 2024. Demonstrating this analytical correlation showcases strong business contextualization."
    )

# TAB 2: Geopolitics & Boycotts
with tab_geopolitics:
    st.subheader("Geopolitical Shockwaves: Boycotts, Wars & Cancellations")
    st.markdown("""
    The Olympic Games have served as a proxy arena for global geopolitics throughout the 20th century.
    Athlete participation plummets during major geopolitical crises and world wars.
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
        height=430,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_geo, use_container_width=True)

    # NEW PLOT: Cold War Superpower Rivalry (1952 – 1988)
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("⚔️ The Cold War Sports Rivalry: USA vs. Soviet Union vs. East Germany (1952 – 1988)")
    st.markdown("""
    During the Cold War, the Olympic medal table was contested as an ideological battlefield between capitalism and state-sponsored athletics programs.
    """)

    cw_df = dl.get_cold_war_rivalry_stats(df, deduplicate=True)
    fig_cw = px.line(
        cw_df,
        x="Year",
        y=[c for c in cw_df.columns if c != 'Year'],
        title="Cold War Olympic Medal Tally (Summer Games 1952 – 1988)",
        markers=True,
        labels={"value": "Official Medals Won", "Year": "Olympic Year", "variable": "Superpower"}
    )
    fig_cw.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20), hovermode="x unified")
    st.plotly_chart(fig_cw, use_container_width=True)

# TAB 3: Growth & Expansion Waves
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
    fig_nat.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_nat, use_container_width=True)

    # NEW PLOT: Debut Nations Waves by Decade
    st.markdown("<br>", unsafe_allow_html=True)
    col_w1, col_w2 = st.columns(2)

    with col_w1:
        st.markdown("#### 🌊 Waves of New Nation Debuts by Decade")
        debut_data = dl.get_debut_nations_by_decade(df)
        fig_debut = px.bar(
            debut_data,
            x="Decade",
            y="New_Nations_Count",
            title="Newly Debuting Nations by Decade",
            labels={"New_Nations_Count": "New Nations Joining", "Decade": "Decade"},
            color="New_Nations_Count",
            color_continuous_scale="Blues"
        )
        fig_debut.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_debut, use_container_width=True)

    with col_w2:
        st.markdown("#### ❄️ Summer vs. Winter Growth Trajectory")
        fig_sw_growth = px.line(
            part_by_year,
            x="Year",
            y="Total_Athletes",
            color="Season",
            title="Summer vs. Winter Athletes Scaling",
            markers=True,
            labels={"Total_Athletes": "Athlete Count", "Year": "Olympic Year"},
            color_discrete_map={"Summer": "#2563eb", "Winter": "#0ea5e9"}
        )
        fig_sw_growth.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_sw_growth, use_container_width=True)

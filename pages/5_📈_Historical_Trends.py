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
    title="📈 Olympic History: Gender Equality, Geopolitics & Global Growth",
    subtitle="Trace how the Olympic Games evolved over 130 years: the long road toward equal participation for women, the impact of world wars and Cold War boycotts, and how new nations joined the global stage.",
    badge="Historical & Geopolitical Trends"
)

# Metrics Ribbon
summer_df = df[df['Season'] == 'Summer']
g_ev = dl.get_gender_evolution(summer_df)

initial_f = g_ev[g_ev['Year'] == 1896]['Female_Pct'].values[0] if not g_ev[g_ev['Year'] == 1896].empty else 0.0
latest_f = g_ev[g_ev['Year'] == 2024]['Female_Pct'].values[0] if not g_ev[g_ev['Year'] == 2024].empty else 0.0
total_nations_peak = summer_df.groupby('Year')['Region'].nunique().max()

tr1, tr2, tr3, tr4 = st.columns(4)
tr1.metric("1896 Women's Share", f"{initial_f:.1f}%", "Women barred from Athens 1896")
tr2.metric("2024 Paris Women's Share", f"{latest_f:.1f}%", "Historic 50/50 Gender Parity")
tr3.metric("Peak Nation Count", f"{total_nations_peak} Nations", "Global Participation")
tr4.metric("Games Cancelled by War", "3 Editions", "1916 (WWI), 1940 & 1944 (WWII)")

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab_gender, tab_geopolitics, tab_growth = st.tabs([
    "⚖️ The Road to Gender Equality",
    "🌍 Geopolitics, Boycotts & Rivalries",
    "🌐 Global Growth & Debuting Nations"
])

# TAB 1: Gender Parity
with tab_gender:
    st.subheader("The Growth of Women's Participation in the Summer Games")
    st.markdown("""
    When the modern Olympics began in Athens in 1896, founder Pierre de Coubertin barred women from competing entirely.
    Over the next 130 years, female athletes steadily broke barriers—from just 22 women competing in tennis and golf in Paris 1900, to the passage of Title IX in the 1970s, all the way to Paris 2024, which became the first Olympic Games in history to achieve an exact 50/50 gender balance.
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
        (1972, 14.6, "1972: US Title IX passed"),
        (1984, 23.0, "1984: First Women's Olympic Marathon"),
        (2012, 44.2, "2012 London: Every national delegation included women"),
        (2024, 49.1, "2024 Paris: Historic 50/50 Gender Balance Milestone")
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

    # Female Medals Won Growth Curve
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🏅 Medals Won by Gender Across Eras")
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
        title="How Women's Representation Reshaped the Games",
        text="The journey toward gender equality in the Olympics took more than a century of persistence. For the first fifty years (1900–1950), women represented fewer than 10% of athletes. A major turning point arrived in the 1970s with landmark equal-opportunity policies like Title IX, which unlocked school funding and athletic scholarships. From that point on, participation surged upward until the 2024 Paris Games finally reached a full 50/50 gender balance."
    )

# TAB 2: Geopolitics & Boycotts
with tab_geopolitics:
    st.subheader("When Geopolitics and World Events Impacted the Games")
    st.markdown("""
    The Olympic Games were never insulated from world events. During the 20th century, world wars forced three Games to be cancelled entirely (1916, 1940, and 1944).
    Later, during the height of the Cold War, geopolitical tensions sparked massive boycotts—such as Montreal 1976, Moscow 1980, and Los Angeles 1984—where dozens of countries stayed home and athlete attendance dropped sharply.
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
        (1980, 5252, "1980 Moscow Boycott (US-led: 66 Nations stayed home)"),
        (1976, 6084, "1976 Montreal Boycott (28 African nations protested apartheid)"),
        (1984, 6791, "1984 Los Angeles Boycott (Soviet-bloc retaliatory boycott)")
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

    # Cold War Superpower Rivalry (1952 – 1988)
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("⚔️ The Cold War Sporting Rivalry (1952 – 1988)")
    st.markdown("""
    Between 1952 and 1988, the Olympic podium became an ideological arena between the United States, the Soviet Union, and East Germany. Each country invested heavily in sports programs, turning every competition into a contest for international prestige.
    """)

    cw_df = dl.get_cold_war_rivalry_stats(df, deduplicate=True)
    fig_cw = px.line(
        cw_df,
        x="Year",
        y=[c for c in cw_df.columns if c != 'Year'],
        title="Cold War Olympic Medal Tally (Summer Games 1952 – 1988)",
        markers=True,
        labels={"value": "Official Medals Won", "Year": "Olympic Year", "variable": "Country"}
    )
    fig_cw.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20), hovermode="x unified")
    st.plotly_chart(fig_cw, use_container_width=True)

# TAB 3: Growth & Expansion Waves
with tab_growth:
    st.subheader("How the World Joined the Olympic Movement")
    
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

    # Debut Nations Waves by Decade
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
        st.markdown("#### ❄️ Summer vs. Winter Growth Over Time")
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

"""
Olympics Athlete Analysis Module
Demographics, peak-performance age curves, longevity, and career lookup.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import data_loader as dl
import ui_utils as ui

st.set_page_config(page_title="Athlete Analysis | Olympics Analytics", page_icon="🏃", layout="wide")
ui.apply_custom_theme()

# Load Data
df = dl.load_olympic_data()

ui.render_hero_banner(
    title="🏃 Athlete Demographics, Longevity & Age Peaks",
    subtitle="Analyze age distributions across sporting disciplines, identify multi-decade persistence, and evaluate all-time Olympian performance profiles.",
    badge="Module 3: Athlete Intelligence"
)

# Key Records Row
rec1, rec2, rec3, rec4 = st.columns(4)
rec1.metric("All-Time Top Medalist", "Michael Phelps (USA)", "28 Medals (23 Gold)")
rec2.metric("Top Female Medalist", "Larisa Latynina (URS)", "18 Medals (9 Gold)")
rec3.metric("Youngest Medalist", "Dimitrios Loundras (GRE)", "Age 10 (Gymnastics, 1896)")
rec4.metric("Oldest Sports Medalist", "Oscar Swahn (SWE)", "Age 72 (Shooting, 1920)")

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab_leaderboard, tab_age, tab_longevity, tab_lookup = st.tabs([
    "🏆 All-Time Olympians",
    "📊 Age-Peak Dynamics by Sport",
    "⏳ Career Longevity & Multi-Games",
    "🔍 Athlete Career Lookup"
])

# TAB 1: Top Olympians
with tab_leaderboard:
    st.subheader("All-Time Most Decorated Olympians")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        gender_filt = st.radio("Filter by Gender:", ["All", "Male", "Female"], horizontal=True, key="ath_gender")
    with col_f2:
        top_n_ath = st.slider("Number of Athletes to Display:", 10, 50, 20, step=5, key="ath_top_n")

    sub_df = df if gender_filt == "All" else df[df['Gender'] == gender_filt]
    top_athletes = dl.get_top_olympians(sub_df, top_n=top_n_ath)

    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        st.dataframe(
            top_athletes[['Rank', 'Name', 'Region', 'Sport', 'Gender', 'Gold', 'Silver', 'Bronze', 'Total', 'Points']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rank": st.column_config.NumberColumn("Rank", width="small"),
                "Name": st.column_config.TextColumn("Athlete Name", width="medium"),
                "Region": "Country",
                "Gold": "🥇 Gold",
                "Silver": "🥈 Silver",
                "Bronze": "🥉 Bronze",
                "Total": "Total",
                "Points": "Weighted Points"
            },
            height=480
        )
    with col_t2:
        fig_ath_bar = px.bar(
            top_athletes.head(15),
            x="Total",
            y="Name",
            orientation='h',
            color="Sport",
            title=f"Top 15 Decorated Olympians ({gender_filt})",
            labels={"Total": "Total Medals Won", "Name": "Athlete"}
        )
        fig_ath_bar.update_layout(yaxis=dict(autorange="reversed"), height=480, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_ath_bar, use_container_width=True)

# TAB 2: Age Dynamics by Sport
with tab_age:
    st.subheader("Biological Peak-Performance Age Curve Across Sports")
    st.markdown("""
    Explore how the peak performance age distribution varies dramatically between high-intensity cardiovascular sports and precision/equestrian sports.
    """)

    sub_age, stats_age = dl.get_age_dynamics_by_sport(df, min_athletes=600)

    # Box Plot
    fig_box = px.box(
        sub_age,
        x="Sport",
        y="Age",
        color="Gender",
        title="Athlete Age Distribution Across Major Olympic Sports",
        labels={"Age": "Athlete Age (Years)", "Sport": "Sport"}
    )
    fig_box.update_layout(height=480, xaxis_tickangle=-45, margin=dict(l=20, r=20, t=40, b=80))
    st.plotly_chart(fig_box, use_container_width=True)

    # Age difference: Medalists vs Non-Medalists
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.markdown("#### Median Age by Sport (Ascending)")
        st.dataframe(
            stats_age[['Sport', 'Median_Age', 'IQR', 'Min_Age', 'Max_Age', 'Count']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Median_Age": st.column_config.NumberColumn("Median Age", format="%.1f yrs"),
                "IQR": st.column_config.NumberColumn("Interquartile Range", format="%.1f"),
                "Min_Age": st.column_config.NumberColumn("Min", format="%d"),
                "Max_Age": st.column_config.NumberColumn("Max", format="%d"),
                "Count": st.column_config.NumberColumn("Sample Records", format="%d")
            },
            height=320
        )

    with c_m2:
        valid_both = df[df['Age'].notna()].copy()
        valid_both['Status'] = np.where(valid_both['Has_Medal'], 'Medal Winner', 'Non-Medal Competitor')
        fig_hist = px.histogram(
            valid_both,
            x="Age",
            color="Status",
            barmode="overlay",
            title="Age Distribution: Medalists vs. Non-Medalists",
            marginal="box",
            opacity=0.6,
            color_discrete_map={"Medal Winner": "#eab308", "Non-Medal Competitor": "#64748b"}
        )
        fig_hist.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_hist, use_container_width=True)

    ui.render_insight_card(
        title="Physical Demands & Career Windows",
        text="The data reveals distinct physiological clusters: Gymnastics and Swimming feature the youngest median ages (20-22 years) due to flexibility and power-to-weight demands, whereas Equestrian and Shooting span athletes well into their late 40s and 50s, proving that fine motor precision and experience outlast raw explosive stamina."
    )

# TAB 3: Longevity & Multi-Games
with tab_longevity:
    st.subheader("Athlete Longevity: Multi-Games Persistence")
    
    ath_editions = df.groupby('Name')['Year'].nunique().value_counts().reset_index()
    ath_editions.columns = ['Editions_Contested', 'Number_of_Athletes']
    ath_editions['Percentage'] = np.round((ath_editions['Number_of_Athletes'] / ath_editions['Number_of_Athletes'].sum()) * 100, 2)
    ath_editions = ath_editions.sort_values(by='Editions_Contested')

    c_lon1, c_lon2 = st.columns([3, 2])
    with c_lon1:
        fig_lon = px.bar(
            ath_editions.head(6),
            x="Editions_Contested",
            y="Number_of_Athletes",
            text="Percentage",
            title="Distribution of Olympic Games Contested per Athlete",
            labels={"Editions_Contested": "Number of Olympic Editions Participated", "Number_of_Athletes": "Athletes Count"}
        )
        fig_lon.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_lon.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_lon, use_container_width=True)

    with c_lon2:
        st.markdown("#### The Elite 1%: Competing Across 5+ Editions")
        legends = df.groupby(['Name', 'Region', 'Sport'])['Year'].agg(
            Editions='nunique',
            Span_Years=lambda x: x.max() - x.min(),
            First_Game='min',
            Last_Game='max'
        ).reset_index()
        top_legends = legends[legends['Editions'] >= 5].sort_values(by=['Editions', 'Span_Years'], ascending=False).head(12)
        st.dataframe(
            top_legends,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Name": "Legend",
                "Region": "Country",
                "Editions": "Games",
                "Span_Years": "Career Span (Yrs)",
                "First_Game": "First",
                "Last_Game": "Last"
            },
            height=320
        )

# TAB 4: Athlete Career Lookup
with tab_lookup:
    st.subheader("🔍 Individual Athlete Profile & Career Timeline")
    
    sample_names = ["Michael Fred Phelps, II", "Usain St. Leo Bolt", "Larisa Semyonovna Latynina (Diriy-)", "Simone Arianne Biles", "Carl Lewis"]
    query = st.text_input("Enter Athlete Name to Search (e.g., Usain Bolt, Michael Phelps, Simone Biles):", value="Usain St. Leo Bolt")

    if query.strip():
        matches = df[df['Name'].str.contains(query, case=False, na=False)]
        if matches.empty:
            st.warning(f"No athlete records matched '{query}'. Try searching for a partial name.")
        else:
            athlete_names = matches['Name'].unique().tolist()
            chosen_athlete = st.selectbox("Select exact athlete:", athlete_names, index=0)

            ath_records = df[df['Name'] == chosen_athlete].sort_values(by=['Year', 'Event'])
            
            # Profile summary
            medals_ath = ath_records[ath_records['Medal'].notna()]
            tot_ath_medals = len(medals_ath)
            g_cnt = len(medals_ath[medals_ath['Medal'] == 'Gold'])
            s_cnt = len(medals_ath[medals_ath['Medal'] == 'Silver'])
            b_cnt = len(medals_ath[medals_ath['Medal'] == 'Bronze'])
            editions_list = sorted(ath_records['Year'].unique())

            p1, p2, p3, p4 = st.columns(4)
            p1.metric("Country", f"{ath_records['Region'].iloc[0]}")
            p2.metric("Sport", f"{ath_records['Sport'].iloc[0]}")
            p3.metric("Total Medals", f"{tot_ath_medals}", f"🥇 {g_cnt} | 🥈 {s_cnt} | 🥉 {b_cnt}")
            p4.metric("Editions Active", f"{len(editions_list)} Games", f"{min(editions_list)} - {max(editions_list)}")

            st.markdown("#### Complete Olympic Event Record")
            st.dataframe(
                ath_records[['Year', 'Season', 'City', 'Sport', 'Event', 'Medal']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Year": st.column_config.NumberColumn("Year", format="%d"),
                    "Medal": st.column_config.TextColumn("Medal Won", help="NaN indicates non-medal participation")
                }
            )

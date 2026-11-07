"""
Olympics India Performance Analytics Module
Provides in-depth diagnostics of India's Olympic journey:
125+ years of records, Field Hockey Dynasty, Modern Multi-Sport Renaissance,
Athlete Hall of Fame, Gender Representation, and Global Benchmarking.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import re
import data_loader as dl
import ui_utils as ui

# 1. Page Configuration
st.set_page_config(page_title="India at Olympics | Olympics Analytics", page_icon="🇮🇳", layout="wide")
ui.apply_custom_theme()

# 2. Data Loading
df = dl.load_olympic_data()
india_df = df[df['Region'] == 'India'].copy()

# 3. Canonical Athlete Name Normalization & Directory
@st.cache_data(show_spinner=False)
def prepare_indian_athletes_catalogue(raw_df):
    """
    Builds a unified Indian athlete directory that resolves name inversions
    across Olympic eras (e.g. Tokyo 2020/Paris 2024 uppercase surnames)
    and enriches recent games records.
    """
    ind = raw_df[raw_df['Region'] == 'India'].copy()

    canonical_aliases = {
        "CHOPRA Neeraj": "Neeraj Chopra",
        "Neeraj CHOPRA": "Neeraj Chopra",
        "Neeraj Chopra": "Neeraj Chopra",
        "Pusarla Venkata \"P. V.\" Sindhu": "PV Sindhu (Pusarla V. Sindhu)",
        "PUSARLA V. Sindhu": "PV Sindhu (Pusarla V. Sindhu)",
        "V. Sindhu PUSARLA": "PV Sindhu (Pusarla V. Sindhu)",
        "MIRABAI Chanu Saikhom": "Mirabai Chanu Saikhom",
        "Mirabai Chanu SAIKHOM": "Mirabai Chanu Saikhom",
        "Saikhom Mirabai Chanu": "Mirabai Chanu Saikhom",
        "BORGOHAIN Lovlina": "Lovlina Borgohain",
        "Lovlina BORGOHAIN": "Lovlina Borgohain",
        "BAJRANG Bajrang": "Bajrang Punia",
        "Bajrang": "Bajrang Punia",
        "Dhyan Chand Bais": "Major Dhyan Chand",
        "Dhyan Chand": "Major Dhyan Chand",
        "Mangte Chungneijang Mary Kom": "MC Mary Kom",
        "HMANGTE Chungneijang Mery Kom": "MC Mary Kom",
        "Khashaba Dadasaheb  Jahdav": "KD Jadhav (Khashaba Jadhav)",
        "Khashaba Dadasaheb \"K. D.\" Jadhav": "KD Jadhav (Khashaba Jadhav)",
        "Parattu Raveendran Sreejesh": "PR Sreejesh",
        "PARATTU RAVEENDRAN Sreejesh": "PR Sreejesh",
        "SINGH Manpreet": "Manpreet Singh",
        "Manpreet SINGH": "Manpreet Singh",
        "SINGH Harmanpreet": "Harmanpreet Singh",
        "Harmanpreet SINGH": "Harmanpreet Singh",
        "BHAKER Manu": "Manu Bhaker",
        "Manu BHAKER": "Manu Bhaker",
        "KUSALE Swapnil": "Swapnil Kusale",
        "SARABJOT Singh": "Sarabjot Singh",
        "ACHANTA Kamal": "Sharath Kamal Achanta",
        "Sharath Kamal ACHANTA": "Sharath Kamal Achanta",
        "BATRA Manika": "Manika Batra",
        "Manika BATRA": "Manika Batra",
        "ASHOK Aditi": "Aditi Ashok",
        "Aditi ASHOK": "Aditi Ashok",
        "SEHRAWAT Aman": "Aman Sehrawat",
        "Norman Gilbert Pritchard (-Trevor)": "Norman Pritchard",
        "Leander Adrian Paes": "Leander Paes",
        "Balbir Singh Dosanjh, Sr.": "Balbir Singh Sr.",
        "Leslie Walter Claudius": "Leslie Claudius",
        "Udham Singh Kular": "Udham Singh",
        "Sushil Kumar Solanki": "Sushil Kumar",
        "Vijender Kumar Singh": "Vijender Singh",
        "Gagan Narang": "Gagan Narang",
        "Rajyavardhan Singh Rathore": "Rajyavardhan Singh Rathore",
        "Karnam Malleswari": "Karnam Malleswari",
        "Saina Nehwal": "Saina Nehwal",
        "Sakshi Malik": "Sakshi Malik",
        "Yogeshwar Dutt": "Yogeshwar Dutt",
        "Ravi Kumar Dahiya": "Ravi Kumar Dahiya",
        "Milkha Singh": "Milkha Singh",
        "Pilavullakandi Thekkeparambil \"P. T.\" Usha": "PT Usha",
        "Abhinav Bindra": "Abhinav Bindra",
    }

    def clean_name(raw):
        raw_str = str(raw).strip()
        if raw_str in canonical_aliases:
            return canonical_aliases[raw_str]
        m = re.match(r'^([A-Z]{2,})\s+([A-Za-z]+.*)$', raw_str)
        if m:
            return f"{m.group(2).strip()} {m.group(1).title().strip()}"
        return raw_str

    ind['Athlete_Name'] = ind['Name'].apply(clean_name)

    # Enrich known Paris 2024 medals for Indian athletes
    paris_2024_medals = {
        ("Neeraj Chopra", 2024): ("Men's Javelin Throw", "Silver"),
        ("Manu Bhaker", 2024): ("Women's 10m Air Pistol", "Bronze"),
        ("Swapnil Kusale", 2024): ("Men's 50m Rifle 3 Positions", "Bronze"),
        ("Aman Sehrawat", 2024): ("Men's Freestyle 57kg", "Bronze"),
        ("Harmanpreet Singh", 2024): ("Men's Field Hockey", "Bronze"),
        ("PR Sreejesh", 2024): ("Men's Field Hockey", "Bronze"),
        ("Manpreet Singh", 2024): ("Men's Field Hockey", "Bronze"),
    }
    for (ath, yr), (ev, med) in paris_2024_medals.items():
        mask = (ind['Athlete_Name'] == ath) & (ind['Year'] == yr)
        if mask.any():
            ind.loc[mask, 'Medal'] = med
            ind.loc[mask, 'Event'] = ev

    # Aggregate career metrics per athlete
    ath_group = ind.groupby('Athlete_Name')
    ath_summary = ath_group.agg(
        Primary_Sport=('Sport', lambda x: x.mode()[0] if not x.empty else 'Olympic Sport'),
        Total_Events=('Event', 'nunique'),
        Editions_Count=('Year', 'nunique'),
        First_Year=('Year', 'min'),
        Last_Year=('Year', 'max'),
        Total_Medals=('Medal', lambda x: x.notna().sum()),
        Gold=('Medal', lambda x: (x == 'Gold').sum()),
        Silver=('Medal', lambda x: (x == 'Silver').sum()),
        Bronze=('Medal', lambda x: (x == 'Bronze').sum()),
    ).reset_index()

    return ind, ath_summary

ind_athletes_records, ind_athletes_summary = prepare_indian_athletes_catalogue(df)

# 4. Hero Banner
ui.render_hero_banner(
    title="🇮🇳 India at the Olympics: 125 Years of History & Triumphs",
    subtitle="From Norman Pritchard's sprint silvers in Paris 1900 and the glorious 8-Gold Field Hockey Dynasty to modern champions across wrestling, shooting, badminton, boxing, and athletics, explore the inspiring journey of Indian Olympians.",
    badge="India Olympic Journey"
)

# 5. Data Precomputations
india_dedup = dl.get_deduplicated_medals(india_df)
tot_dedup_medals = len(india_dedup)
tot_raw_medals = india_df['Medal'].notna().sum()
tot_gold = (india_dedup['Medal'] == 'Gold').sum()
tot_silver = (india_dedup['Medal'] == 'Silver').sum()
tot_bronze = (india_dedup['Medal'] == 'Bronze').sum()
tot_athletes = india_df['Name'].nunique()
editions_count = india_df['Year'].nunique()

# Global All-time Tally for Rank Calculation
all_time_tally = dl.get_medal_tally(df, year='All-Time', season='All', deduplicate=True)
india_rank_row = all_time_tally[all_time_tally['Region'] == 'India']
india_rank = int(india_rank_row['Rank'].iloc[0]) if not india_rank_row.empty else "N/A"
india_points = int(india_rank_row['Points'].iloc[0]) if not india_rank_row.empty else "N/A"

# 6. Executive KPI Ribbon
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("All-Time Global Rank", f"#{india_rank}", f"{india_points} Weighted Points")
k2.metric("Official Event Medals", f"{tot_dedup_medals}", f"{tot_raw_medals} Raw Medals", help="Counted once per team event to reflect official IOC podiums")
k3.metric("🥇 Gold Medals", f"{tot_gold}", "8 Hockey | 1 Shooting | 1 Athletics")
k4.metric("🥈 Silver Medals", f"{tot_silver}", "Athletics, Shooting, Wrestling, Weightlifting, Badminton")
k5.metric("🥉 Bronze Medals", f"{tot_bronze}", "Hockey, Wrestling, Boxing, Badminton, Tennis")
k6.metric("Unique Olympians Sent", f"{tot_athletes:,}", f"{editions_count} Olympic Editions")

st.markdown("<br>", unsafe_allow_html=True)

# 7. Analytical Tabs
tab_traj, tab_sports, tab_legends, tab_gender, tab_global = st.tabs([
    "📈 Medal History & The 4 Eras",
    "🏑 Sports & The Modern Shift",
    "🎖️ Hall of Fame & Athlete Search",
    "👩 Women Champions & Representation",
    "🌐 Global Standing & Future Horizons"
])

# ==============================================================================
# TAB 1: HISTORICAL TRAJECTORY & ERAS
# ==============================================================================
with tab_traj:
    st.subheader("📈 India's Medal Progression Over Time (1900 – Present)")
    st.markdown("""
    Follow how India's medal hauls developed over the decades, transitioning from decades of field hockey mastery to a vibrant multi-sport presence in recent Games.
    """)

    yearly_ind = dl.get_country_yearly_stats(df, 'India', deduplicate=True)
    summer_yearly = yearly_ind[yearly_ind['Season'] == 'Summer'].sort_values('Year')

    col_t1, col_t2 = st.columns([3, 2])

    with col_t1:
        # Stacked bar of medals per edition
        fig_med_trend = go.Figure()
        fig_med_trend.add_trace(go.Bar(
            x=summer_yearly['Year'], y=summer_yearly['Bronze'],
            name='Bronze', marker_color='#CD7F32'
        ))
        fig_med_trend.add_trace(go.Bar(
            x=summer_yearly['Year'], y=summer_yearly['Silver'],
            name='Silver', marker_color='#C0C0C0'
        ))
        fig_med_trend.add_trace(go.Bar(
            x=summer_yearly['Year'], y=summer_yearly['Gold'],
            name='Gold', marker_color='#FFD700'
        ))
        fig_med_trend.update_layout(
            barmode='stack',
            title="Official Medals Won by Olympic Edition (Summer Games)",
            xaxis_title="Olympic Year",
            yaxis_title="Official Medals",
            height=420,
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode="x unified"
        )
        st.plotly_chart(fig_med_trend, use_container_width=True)

    with col_t2:
        # Athletes Sent vs Conversion Rate
        fig_scaling = go.Figure()
        fig_scaling.add_trace(go.Bar(
            x=summer_yearly['Year'], y=summer_yearly['Athletes_Sent'],
            name='Contingent Size (Athletes)', marker_color='#93c5fd', opacity=0.7
        ))
        fig_scaling.add_trace(go.Scatter(
            x=summer_yearly['Year'], y=summer_yearly['Total_Medals'],
            name='Medals Won', mode='lines+markers', line=dict(color='#ef4444', width=3),
            yaxis='y2'
        ))
        fig_scaling.update_layout(
            title="Contingent Size vs. Medals Won",
            xaxis_title="Olympic Year",
            yaxis=dict(title="Athletes Sent"),
            yaxis2=dict(title="Medals Won", overlaying='y', side='right', showgrid=False),
            height=420,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(x=0.02, y=0.98)
        )
        st.plotly_chart(fig_scaling, use_container_width=True)

    # The 4 Historical Eras of Indian Olympic Sport
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🏛️ The Four Historical Eras of Indian Olympic History")

    era1, era2, era3, era4 = st.columns(4)
    with era1:
        st.markdown("""
        **1. The Early Years (1900 – 1920)**  
        - **Norman Pritchard (1900):** Won 2 Silver medals in the 200m and 200m Hurdles in Paris.  
        - In 1920, Sir Dorabji Tata organized India's first official multi-sport contingent for the Antwerp Games.
        """)
    with era2:
        st.markdown("""
        **2. The Golden Hockey Era (1928 – 1980)**  
        - **6 Consecutive Golds** (1928–1956) during an extraordinary 30-match winning streak.  
        - Won **8 Olympic Gold medals** in Field Hockey overall (1928, '32, '36, '48, '52, '56, '64, '80).  
        - **KD Jadhav (1952):** Won an iconic Freestyle Wrestling Bronze in Helsinki, becoming independent India's first individual medalist.
        """)
    with era3:
        st.markdown("""
        **3. The Transition & Rebuilding (1984 – 1996)**  
        - The introduction of artificial AstroTurf shifted the dynamics of international hockey.  
        - **PT Usha (1984):** Missed the 400m hurdles bronze in Los Angeles by just 1/100th of a second.  
        - **Leander Paes (1996):** Captured Bronze in Men's Singles Tennis at Atlanta, ending a 44-year individual medal drought.
        """)
    with era4:
        st.markdown("""
        **4. The Modern Multi-Sport Era (2000 – Present)**  
        - **Karnam Malleswari (2000):** Made history as India's first female Olympic medalist (Weightlifting Bronze).  
        - **Abhinav Bindra (2008):** Won India's first individual Gold medal in Beijing (10m Air Rifle).  
        - **Tokyo 2020 Milestone:** Best-ever haul of 7 medals, headlined by **Neeraj Chopra's** historic Athletics Gold!
        """)

    ui.render_insight_card(
        title="How India Broadened Its Sporting Horizons",
        text="For much of the 20th century, India's medal hopes rested almost entirely on the shoulders of the Men's Field Hockey team. That landscape changed dramatically over the last two decades. The creation of national training initiatives like the Target Olympic Podium Scheme (TOPS), along with non-profit sports foundations, brought world-class coaching, sports psychology, and international exposure to athletes across diverse events. That groundwork paid off with landmark multi-medal achievements in London 2012 (6 medals) and Tokyo 2020 (7 medals)."
    )

# ==============================================================================
# TAB 2: SPORT SPECIALIZATION & DISCIPLINE SHIFT
# ==============================================================================
with tab_sports:
    st.subheader("🏑 Sports That Delivered Medals")
    st.markdown("""
    See which sports contributed most to India's medal haul, and explore how success branched out from field hockey into a wide range of individual sports in the 21st century.
    """)

    sport_medals = india_dedup.groupby(['Sport', 'Medal']).size().unstack(fill_value=0).reset_index()
    for m in ['Gold', 'Silver', 'Bronze']:
        if m not in sport_medals.columns:
            sport_medals[m] = 0
    sport_medals['Total'] = sport_medals['Gold'] + sport_medals['Silver'] + sport_medals['Bronze']
    sport_medals = sport_medals.sort_values(by='Total', ascending=False)

    col_s1, col_s2 = st.columns([1, 1])

    with col_s1:
        # Horizontal bar chart of medals by sport
        fig_sp_bar = px.bar(
            sport_medals,
            x=["Gold", "Silver", "Bronze"],
            y="Sport",
            orientation='h',
            title="Official Medals Won by Sporting Discipline",
            color_discrete_map={"Gold": "#FFD700", "Silver": "#C0C0C0", "Bronze": "#CD7F32"},
            barmode="stack",
            labels={"value": "Medal Count", "Sport": "Sporting Discipline"}
        )
        fig_sp_bar.update_layout(yaxis=dict(autorange="reversed"), height=440, margin=dict(l=20, r=20, t=40, b=20), legend_title="")
        st.plotly_chart(fig_sp_bar, use_container_width=True)

    with col_s2:
        # Pre-2000 vs Post-2000 Shift Pie / Donut
        post_2000 = india_dedup[india_dedup['Year'] >= 2000]

        shift_df = pd.DataFrame([
            {"Sport": "Hockey", "Count": len(post_2000[post_2000['Sport'] == 'Hockey'])},
            {"Sport": "Wrestling", "Count": len(post_2000[post_2000['Sport'] == 'Wrestling'])},
            {"Sport": "Shooting", "Count": len(post_2000[post_2000['Sport'] == 'Shooting'])},
            {"Sport": "Badminton", "Count": len(post_2000[post_2000['Sport'] == 'Badminton'])},
            {"Sport": "Boxing", "Count": len(post_2000[post_2000['Sport'] == 'Boxing'])},
            {"Sport": "Weightlifting", "Count": len(post_2000[post_2000['Sport'] == 'Weightlifting'])},
            {"Sport": "Athletics", "Count": len(post_2000[post_2000['Sport'] == 'Athletics'])},
        ])

        fig_shift = px.pie(
            shift_df,
            names="Sport",
            values="Count",
            hole=0.45,
            title="The 21st Century Shift: Medals Won Since 2000 by Sport",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_shift.update_traces(textposition='inside', textinfo='percent+label')
        fig_shift.update_layout(height=440, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_shift, use_container_width=True)

    # Treemap of India's Medals Hierarchy
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🌳 India's Olympic Medal Hierarchy (Sport → Event → Tier)")
    
    tree_data = india_dedup.groupby(['Sport', 'Event', 'Medal']).size().reset_index(name='Medal_Count')
    fig_ind_tree = px.treemap(
        tree_data,
        path=['Sport', 'Medal', 'Event'],
        values='Medal_Count',
        color='Medal',
        color_discrete_map={"Gold": "#eab308", "Silver": "#94a3b8", "Bronze": "#b45309", "(?)": "#3b82f6"},
        title="India Olympic Podium Hierarchy (Event-Level Deduplicated)"
    )
    fig_ind_tree.update_layout(height=480, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_ind_tree, use_container_width=True)

    # Hockey Dynasty Deep Dive
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🏑 Field Hockey: The Dynasty That Defined an Era")
    
    h_col1, h_col2, h_col3 = st.columns(3)
    h_col1.metric("Olympic Hockey Medals", "12 Medals", "8 Gold | 1 Silver | 3 Bronze")
    h_col2.metric("Consecutive Golds", "6 Editions (1928–1956)", "30 Consecutive Match Wins")
    h_col3.metric("Goal Differential (1928)", "29 Goals Scored, 0 Conceded", "Led by Major Dhyan Chand")

# ==============================================================================
# TAB 3: HALL OF FAME & ATHLETE EXPLORER
# ==============================================================================
with tab_legends:
    st.subheader("🎖️ India's Olympic Legends & Individual Multi-Medalists")
    st.markdown("""
    Celebrate India's most decorated Olympians, explore athletes who won multiple medals, and look up career records for any Indian Olympian across 130 years.
    """)

    # Multi-Medalist Spotlight Ribbon
    st.markdown("#### 🌟 Individual Multi-Medalists in Indian History")
    leg1, leg2, leg3, leg4 = st.columns(4)
    leg1.metric("Norman Pritchard", "2 Medals (Paris 1900)", "🥈 200m | 🥈 200m Hurdles")
    leg2.metric("Sushil Kumar", "2 Medals (2008, 2012)", "🥉 Beijing | 🥈 London (Wrestling)")
    leg3.metric("PV Sindhu", "2 Medals (2016, 2020)", "🥈 Rio | 🥉 Tokyo (Badminton)")
    leg4.metric("Neeraj Chopra", "2 Medals (2020, 2024)", "🥇 Tokyo | 🥈 Paris (Javelin)")

    st.markdown("<br>", unsafe_allow_html=True)

    # Master Table of Indian Medalists
    st.markdown("#### 📋 Complete Ledger of Indian Olympic Medals")
    
    medalist_records = india_dedup.copy()
    medalist_records['Athlete_Display'] = np.where(
        medalist_records['Sport'] == 'Hockey',
        "Indian National Hockey Squad",
        medalist_records['Name']
    )
    
    display_ledger = medalist_records[['Year', 'Season', 'City', 'Sport', 'Event', 'Medal', 'Athlete_Display', 'Gender']].sort_values(
        by=['Year', 'Medal'], ascending=[False, True]
    ).reset_index(drop=True)

    st.dataframe(
        display_ledger,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Year": st.column_config.NumberColumn("Year", format="%d", width="small"),
            "City": "Host City",
            "Sport": "Sport",
            "Event": st.column_config.TextColumn("Event", width="medium"),
            "Medal": st.column_config.TextColumn("Medal", width="small"),
            "Athlete_Display": st.column_config.TextColumn("Medalist(s)", width="large"),
            "Gender": "Category"
        },
        height=400
    )

    # --------------------------------------------------------------------------
    # Interactive Indian Athlete Search & Career Lookup (Dropdown of ALL Athletes)
    # --------------------------------------------------------------------------
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🔍 Indian Olympian Career Lookup & Visual Timeline")
    st.markdown("""
    Select any Indian Olympian from the dropdown below to explore their complete career history, Olympic appearances, events contested, and medal achievements:
    """)

    # Quick Filters Row
    col_filter1, col_filter2 = st.columns([1, 1])

    with col_filter1:
        all_sports_options = ["All Sports"] + sorted(ind_athletes_summary['Primary_Sport'].dropna().unique().tolist())
        filter_sport = st.selectbox("Filter Athletes by Sport:", all_sports_options, index=0)

    with col_filter2:
        filter_cat = st.selectbox(
            "Filter Athletes by Category:",
            ["All Athletes", "Medal Winners Only (🏆)", "Multi-Games Olympians (2+ Games)"],
            index=0
        )

    # Filter athlete summary
    filtered_summary = ind_athletes_summary.copy()
    if filter_sport != "All Sports":
        filtered_summary = filtered_summary[filtered_summary['Primary_Sport'] == filter_sport]

    if filter_cat == "Medal Winners Only (🏆)":
        filtered_summary = filtered_summary[filtered_summary['Total_Medals'] > 0]
    elif filter_cat == "Multi-Games Olympians (2+ Games)":
        filtered_summary = filtered_summary[filtered_summary['Editions_Count'] >= 2]

    # Sort alphabetically by athlete name
    filtered_summary = filtered_summary.sort_values(by='Athlete_Name').reset_index(drop=True)

    if filtered_summary.empty:
        st.warning("No Indian Olympians match the chosen filter combination. Try selecting 'All Sports' or 'All Athletes'.")
    else:
        # Create display labels for the dropdown
        label_dict = {}
        for _, r in filtered_summary.iterrows():
            name = r['Athlete_Name']
            sport = r['Primary_Sport']
            tot_m = r['Total_Medals']
            ed_cnt = r['Editions_Count']
            if tot_m > 0:
                med_badges = []
                if r['Gold'] > 0: med_badges.append(f"🥇 {r['Gold']}")
                if r['Silver'] > 0: med_badges.append(f"🥈 {r['Silver']}")
                if r['Bronze'] > 0: med_badges.append(f"🥉 {r['Bronze']}")
                label_dict[name] = f"{name} ({sport} | {' '.join(med_badges)})"
            elif ed_cnt > 1:
                label_dict[name] = f"{name} ({sport} | {ed_cnt} Olympic Games)"
            else:
                label_dict[name] = f"{name} ({sport} | {r['First_Year']})"

        athlete_names_list = filtered_summary['Athlete_Name'].tolist()

        # Choose intuitive default athlete
        default_idx = 0
        if "Neeraj Chopra" in athlete_names_list:
            default_idx = athlete_names_list.index("Neeraj Chopra")
        elif "Major Dhyan Chand" in athlete_names_list:
            default_idx = athlete_names_list.index("Major Dhyan Chand")

        chosen_athlete = st.selectbox(
            f"Select Indian Olympian ({len(athlete_names_list):,} athletes available):",
            athlete_names_list,
            index=default_idx,
            format_func=lambda n: label_dict.get(n, n)
        )

        # Retrieve all historical records for chosen athlete
        ath_records = ind_athletes_records[ind_athletes_records['Athlete_Name'] == chosen_athlete].sort_values(by=['Year', 'Event']).copy()
        ath_info = filtered_summary[filtered_summary['Athlete_Name'] == chosen_athlete].iloc[0]

        # Athlete Overview Metric Ribbon
        st.markdown("<br>", unsafe_allow_html=True)
        p1, p2, p3, p4, p5 = st.columns(5)
        p1.metric("Sport", f"{ath_info['Primary_Sport']}")
        
        med_badge_str = f"🥇 {ath_info['Gold']} | 🥈 {ath_info['Silver']} | 🥉 {ath_info['Bronze']}" if ath_info['Total_Medals'] > 0 else "Best: Participant"
        p2.metric("Total Medals", f"{ath_info['Total_Medals']}", med_badge_str)
        
        ed_years = sorted(ath_records['Year'].unique().tolist())
        ed_str = f"{min(ed_years)} – {max(ed_years)}" if len(ed_years) > 1 else str(ed_years[0])
        p3.metric("Olympic Editions", f"{ath_info['Editions_Count']} Games", ed_str)
        p4.metric("Events Contested", f"{ath_info['Total_Events']}")
        p5.metric("Career Span", f"{max(ed_years) - min(ed_years)} Years" if len(ed_years) > 1 else "1 Games")

        # Podium Achievements & Milestones Callout
        ath_medals = ath_records[ath_records['Medal'].notna()]
        if not ath_medals.empty:
            med_lines = []
            for _, m_row in ath_medals.iterrows():
                icon = "🥇" if m_row['Medal'] == 'Gold' else ("🥈" if m_row['Medal'] == 'Silver' else "🥉")
                med_lines.append(f"**{icon} {m_row['Medal']} Medal** — {m_row['Event']} ({m_row['City']} {m_row['Year']})")
            st.success("🌟 **Olympic Podium Achievements:**  \n" + "  \n".join(med_lines))

        if ath_info['Editions_Count'] >= 3:
            st.info(f"🏛️ **Olympic Veteran:** Represented India across **{ath_info['Editions_Count']} Olympic Games** ({', '.join(str(y) for y in ed_years)}) spanning {max(ed_years) - min(ed_years)} years.")

        # Visual Career Timeline Plot
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"#### 📅 Visual Olympic Timeline: {chosen_athlete}")

        timeline_df = ath_records.copy()
        timeline_df['Medal_Status'] = timeline_df['Medal'].fillna('Participation (Non-Medal)')
        timeline_df['Point_Size'] = 16
        timeline_df['Edition_Label'] = timeline_df['Year'].astype(str) + " " + timeline_df['City']

        fig_ind_time = px.scatter(
            timeline_df,
            x="Year",
            y="Event",
            color="Medal_Status",
            size="Point_Size",
            hover_name="Edition_Label",
            hover_data={
                "Year": True,
                "City": True,
                "Sport": True,
                "Event": True,
                "Medal_Status": True,
                "Point_Size": False
            },
            title=f"Olympic Event Timeline: {chosen_athlete}",
            color_discrete_map={
                "Gold": "#FFD700",
                "Silver": "#C0C0C0",
                "Bronze": "#CD7F32",
                "Participation (Non-Medal)": "#3b82f6"
            }
        )

        if len(ed_years) == 1:
            yr = ed_years[0]
            fig_ind_time.update_xaxes(
                tickmode='array',
                tickvals=[yr],
                ticktext=[f"{yr}<br>{ath_records['City'].iloc[0]}"],
                range=[yr - 2, yr + 2]
            )
        else:
            year_labels = [f"{y}<br>{ath_records[ath_records['Year'] == y]['City'].iloc[0]}" for y in ed_years]
            fig_ind_time.update_xaxes(
                tickmode='array',
                tickvals=ed_years,
                ticktext=year_labels,
                range=[min(ed_years) - 2, max(ed_years) + 2]
            )

        fig_ind_time.update_traces(marker=dict(line=dict(width=1.5, color='#ffffff')))
        fig_ind_time.update_layout(
            height=max(320, 45 * len(ath_records['Event'].unique()) + 140),
            margin=dict(l=20, r=20, t=40, b=20),
            yaxis=dict(title="Event", autorange="reversed")
        )
        st.plotly_chart(fig_ind_time, use_container_width=True)

        # Complete Career Ledger Table
        st.markdown(f"#### 📋 Complete Career Ledger ({len(ath_records)} Participations)")

        ath_records['Result'] = ath_records['Medal'].apply(
            lambda m: "🥇 Gold" if m == "Gold" else ("🥈 Silver" if m == "Silver" else ("🥉 Bronze" if m == "Bronze" else "Participant"))
        )

        display_ledger_table = ath_records[['Year', 'City', 'Season', 'Sport', 'Event', 'Result', 'Age']].sort_values(
            by=['Year', 'Event'], ascending=[False, True]
        )

        st.dataframe(
            display_ledger_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Year": st.column_config.NumberColumn("Year", format="%d", width="small"),
                "City": "Host City",
                "Season": "Season",
                "Sport": "Sport",
                "Event": st.column_config.TextColumn("Event", width="medium"),
                "Result": st.column_config.TextColumn("Olympic Result", width="medium"),
                "Age": st.column_config.NumberColumn("Age at Games", format="%d")
            }
        )

# ==============================================================================
# TAB 4: GENDER EVOLUTION & WOMEN CHAMPIONS
# ==============================================================================
with tab_gender:
    st.subheader("👩 Women Athletes in Indian Olympic Delegations")
    st.markdown("""
    Follow the inspiring rise of female athletes in Indian contingents, and celebrate the trailblazing women who won medals on the world stage.
    """)

    # Gender share over time
    gender_evolution = india_df[india_df['Season'] == 'Summer'].groupby(['Year', 'Gender'])['Name'].nunique().unstack(fill_value=0).reset_index()
    if 'Female' not in gender_evolution.columns:
        gender_evolution['Female'] = 0
    if 'Male' not in gender_evolution.columns:
        gender_evolution['Male'] = 0

    gender_evolution['Total'] = gender_evolution['Female'] + gender_evolution['Male']
    gender_evolution['Female_Pct'] = np.round((gender_evolution['Female'] / gender_evolution['Total']) * 100, 1)

    col_g1, col_g2 = st.columns([3, 2])

    with col_g1:
        fig_gen_ind = go.Figure()
        fig_gen_ind.add_trace(go.Scatter(
            x=gender_evolution['Year'],
            y=gender_evolution['Female_Pct'],
            mode='lines+markers',
            name='Female Athlete Share (%)',
            line=dict(color='#ec4899', width=3),
            marker=dict(size=7)
        ))
        fig_gen_ind.update_layout(
            title="Percentage of Women Athletes in Indian Summer Delegations",
            xaxis_title="Olympic Year",
            yaxis_title="Female Athlete %",
            yaxis=dict(range=[0, 60]),
            height=420,
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode="x unified"
        )
        st.plotly_chart(fig_gen_ind, use_container_width=True)

    with col_g2:
        # Stacked bar of athlete volume by gender
        fig_vol_ind = px.bar(
            gender_evolution,
            x="Year",
            y=["Male", "Female"],
            title="Indian Athletes Sent by Gender Over Time",
            color_discrete_map={"Male": "#3b82f6", "Female": "#ec4899"},
            barmode="stack",
            labels={"value": "Athletes", "Year": "Year"}
        )
        fig_vol_ind.update_layout(height=420, margin=dict(l=20, r=20, t=40, b=20), legend_title="")
        st.plotly_chart(fig_vol_ind, use_container_width=True)

    # Modern Era Women Medals Highlight
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("⭐ The Women Who Shaped Modern Indian Olympic History")

    w_medals_modern = india_dedup[(india_dedup['Year'] >= 2000) & (india_dedup['Gender'] == 'Female')]
    m_medals_modern = india_dedup[(india_dedup['Year'] >= 2000) & (india_dedup['Gender'] == 'Male')]

    wm_col1, wm_col2, wm_col3 = st.columns(3)
    wm_col1.metric("Women's Medals Since 2000", f"{len(w_medals_modern)} Medals", "Across 5 Unique Sports")
    wm_col2.metric("Men's Medals Since 2000", f"{len(m_medals_modern)} Medals", "Across 4 Unique Sports")
    wm_col3.metric("Women's Share of Modern Podiums", f"{round(len(w_medals_modern) / (len(w_medals_modern) + len(m_medals_modern)) * 100, 1)}%", "High Podium Success Rate")

    st.markdown("""
    - **Karnam Malleswari (Sydney 2000):** Bronze in Weightlifting (69kg) — *Became the first Indian woman to ever win an Olympic medal*.
    - **Mary Kom (London 2012):** Bronze in Flyweight Boxing — The 6-time World Champion made Olympic boxing history in the debut of women's boxing.
    - **Saina Nehwal (London 2012):** Bronze in Women's Singles — Won India's first Olympic medal in Badminton.
    - **PV Sindhu (Rio 2016 & Tokyo 2020):** Silver (2016) & Bronze (2020) — *Became the first Indian woman to win medals at two consecutive Olympic Games*.
    - **Sakshi Malik (Rio 2016):** Bronze in 58kg Freestyle — Became India's first female wrestler to stand on the Olympic podium.
    - **Mirabai Chanu (Tokyo 2020):** Silver in 49kg Weightlifting — Opened India's Tokyo medal count on the very first day.
    - **Lovlina Borgohain (Tokyo 2020):** Bronze in Welterweight Boxing in her Olympic debut.
    """)

# ==============================================================================
# TAB 5: GLOBAL STANDING & BENCHMARKING
# ==============================================================================
with tab_global:
    st.subheader("🌐 Global Standing & Future Horizons")
    st.markdown("""
    See how India compares against peer emerging sporting nations, and explore the strategic avenues that can help Indian athletes win more medals in future Games.
    """)

    # Select peer nations for benchmark
    peer_defaults = ["India", "Brazil", "South Africa", "Thailand", "Indonesia", "Turkey", "Egypt"]
    peer_options = sorted(list(set(all_time_tally['Region'].unique().tolist() + peer_defaults)))
    
    selected_peers = st.multiselect(
        "Select Nations to Benchmark Against:",
        peer_options,
        default=[p for p in peer_defaults if p in peer_options]
    )

    if selected_peers:
        peer_tally = all_time_tally[all_time_tally['Region'].isin(selected_peers)].sort_values(by='Points', ascending=False)
        
        col_b1, col_b2 = st.columns([3, 2])

        with col_b1:
            fig_peer = px.bar(
                peer_tally,
                x="Region",
                y=["Gold", "Silver", "Bronze"],
                title="All-Time Medal Comparison Across Peer Sporting Nations",
                color_discrete_map={"Gold": "#FFD700", "Silver": "#C0C0C0", "Bronze": "#CD7F32"},
                barmode="stack",
                labels={"value": "Official Medals", "Region": "Nation"}
            )
            fig_peer.update_layout(height=420, margin=dict(l=20, r=20, t=40, b=20), legend_title="")
            st.plotly_chart(fig_peer, use_container_width=True)

        with col_b2:
            st.markdown("#### Peer Benchmark Table")
            st.dataframe(
                peer_tally[['Rank', 'Region', 'Gold', 'Silver', 'Bronze', 'Total', 'Points']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Rank": st.column_config.NumberColumn("Global Rank", width="small"),
                    "Region": "Nation",
                    "Points": st.column_config.NumberColumn("Weighted Pts", format="%d")
                },
                height=360
            )

    # Strategic Diagnostic
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("💡 Strategic Reflections: The Road Ahead for Indian Sports")

    s1, s2 = st.columns(2)
    with s1:
        st.markdown("""
        #### 🚀 Key Strengths & Proven Success
        1. **Deep Grassroots in Niche Sports:** Wrestling (7 medals) and Shooting (4 medals) demonstrated consistent medal output across multiple Olympic cycles.
        2. **Remarkable Impact of Female Athletes:** Women athletes delivered outstanding podium conversion rates, particularly in badminton, boxing, and weightlifting.
        3. **Breaking Barriers in Track and Field:** Neeraj Chopra's Javelin Gold (2020) and Silver (2024) proved that Indian athletes can compete and win at the highest level in athletics.
        """)
    with s2:
        st.markdown("""
        #### 🎯 Opportunities for Greater Growth
        1. **Competing in Medal-Rich Sports:** Disciplines like Swimming, Gymnastics, Rowing, and Cycling account for over 45% of all Olympic medals. Expanding talent pipelines in these sports offers enormous potential.
        2. **Turning Near-Misses into Podiums:** India historically recorded several heartbreaking fourth-place finishes (Milkha Singh in 1960, PT Usha in 1984, Dipa Karmakar in 2016, and Sania Mirza/Rohan Bopanna in 2016). Targeted sports psychology, mental conditioning, and tournament exposure help close this narrow gap.
        3. **Hosting the Olympic Games:** Historical data showed that host nations gained an average +50% or greater medal increase, driven by automatic qualifications and long-term sports infrastructure funding.
        """)

    ui.render_insight_card(
        title="The Big Picture: India's Path Forward",
        text="India's Olympic journey showed an inspiring transition from a single-sport powerhouse to a multifaceted sporting nation. The data demonstrated that targeted funding, sports science, and grassroots training turned potential into podiums. Looking ahead, expanding participation in medal-rich sports like swimming, track and field, and gymnastics will be key to helping Indian athletes reach even higher on the global leaderboard."
    )

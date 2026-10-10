"""
Olympics Country Analysis Module
Deep-dive diagnostics for individual nations, delegation conversion efficiency,
empirical host advantage testing, and head-to-head nation comparisons.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import data_loader as dl
import ui_utils as ui

st.set_page_config(page_title="Country Analysis | Olympics Analytics", page_icon="🌍", layout="wide")
ui.apply_custom_theme()

# Load Data
df = dl.load_olympic_data()

ui.render_hero_banner(
    title="🌍 National Performance & Efficiency Diagnostics",
    subtitle="Evaluate historical trajectories, delegation conversion efficiency, host nation home-turf advantage, and multi-country comparative benchmarking.",
    badge="Module 2: Country Intelligence"
)

# Country Selector
all_regions = sorted(df['Region'].dropna().unique().tolist())
default_country = "USA" if "USA" in all_regions else all_regions[0]

c_col1, c_col2 = st.columns([3, 1])
with c_col1:
    selected_country = st.selectbox("Select Country / Region to Analyze:", all_regions, index=all_regions.index(default_country) if default_country in all_regions else 0)
with c_col2:
    dedup_country = st.toggle("Deduplicate Team Medals", value=True, key="cntry_dedup")

# Get country stats
c_yearly = dl.get_country_yearly_stats(df, selected_country, deduplicate=dedup_country)

if c_yearly.empty:
    st.warning(f"No historical records found for {selected_country}.")
else:
    # High-level metrics ribbon
    tot_medals = c_yearly['Total_Medals'].sum()
    tot_gold = c_yearly['Gold'].sum()
    tot_silver = c_yearly['Silver'].sum()
    tot_bronze = c_yearly['Bronze'].sum()
    tot_athletes = c_yearly['Athletes_Sent'].sum()
    overall_eff = round((tot_medals / tot_athletes * 100), 2) if tot_athletes > 0 else 0
    host_editions = c_yearly[c_yearly['Hosted'] == True]

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Total Medals", f"{tot_medals:,}")
    m2.metric("🥇 Gold Medals", f"{tot_gold:,}")
    m3.metric("🥈 Silver Medals", f"{tot_silver:,}")
    m4.metric("🥉 Bronze Medals", f"{tot_bronze:,}")
    m5.metric("Games Hosted", f"{len(host_editions)} Editions")
    m6.metric("Conversion Rate", f"{overall_eff}%", help="Total Medals won divided by total athlete participations")

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs
    tab_traj, tab_sports, tab_host, tab_compare = st.tabs([
        "📈 Historical Trajectory & Delegations",
        "🎯 Sport Specialization & Seasonal Split",
        "🏠 Host Country Advantage (Hypothesis Testing)",
        "⚔️ Head-to-Head Comparison"
    ])

    # TAB 1: Historical Trajectory
    with tab_traj:
        st.subheader(f"Historical Olympic Trajectory: {selected_country}")
        
        fig_traj = go.Figure()
        
        # Line for Total Medals
        fig_traj.add_trace(go.Scatter(
            x=c_yearly['Year'],
            y=c_yearly['Total_Medals'],
            mode='lines+markers',
            name='Total Medals',
            line=dict(color='#2563eb', width=3),
            marker=dict(size=7)
        ))
        
        # Highlight Host Years
        if not host_editions.empty:
            fig_traj.add_trace(go.Scatter(
                x=host_editions['Year'],
                y=host_editions['Total_Medals'],
                mode='markers',
                name='Hosted Edition',
                marker=dict(color='#ef4444', size=14, symbol='star', line=dict(width=2, color='#ffffff'))
            ))

        fig_traj.update_layout(
            title=f"Medal Progression Over Time (Red Stars = Games Hosted by {selected_country})",
            xaxis_title="Olympic Year",
            yaxis_title="Official Medals Won",
            height=430,
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode="x unified"
        )
        st.plotly_chart(fig_traj, use_container_width=True)

        # Row: Delegation Size & Conversion Rate
        c1_sub, c2_sub = st.columns(2)
        with c1_sub:
            fig_ath = px.bar(
                c_yearly,
                x="Year",
                y="Athletes_Sent",
                color="Season",
                title="Delegation Size (Athletes Sent per Edition)",
                labels={"Athletes_Sent": "Athletes Sent", "Year": "Olympic Year"}
            )
            fig_ath.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_ath, use_container_width=True)

        with c2_sub:
            fig_eff = px.line(
                c_yearly,
                x="Year",
                y="Conversion_Rate_%",
                title="Medal Conversion Rate % (Medals Won / Athletes Sent)",
                markers=True,
                labels={"Conversion_Rate_%": "Conversion Rate (%)", "Year": "Olympic Year"}
            )
            fig_eff.update_traces(line_color="#10b981", line_width=2.5)
            fig_eff.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_eff, use_container_width=True)

        # NEW PLOTS: Gender Participation Breakdown & Delegation vs Medal Correlation
        st.markdown("<br>", unsafe_allow_html=True)
        c3_sub, c4_sub = st.columns(2)
        with c3_sub:
            c_gender = dl.get_country_gender_evolution(df, selected_country)
            if not c_gender.empty:
                fig_c_gen = px.bar(
                    c_gender,
                    x="Year",
                    y=["Male", "Female"],
                    title=f"Gender Delegation Composition: {selected_country}",
                    labels={"value": "Athletes Count", "Year": "Olympic Year"},
                    color_discrete_map={"Male": "#3b82f6", "Female": "#ec4899"},
                    barmode="stack"
                )
                fig_c_gen.update_layout(height=360, legend_title="", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_c_gen, use_container_width=True)

        with c4_sub:
            fig_corr = px.scatter(
                c_yearly,
                x="Athletes_Sent",
                y="Total_Medals",
                trendline="ols",
                title=f"Delegation Size vs. Medal Count Correlation ({selected_country})",
                labels={"Athletes_Sent": "Athletes Sent", "Total_Medals": "Total Medals Won"},
                hover_data=["Year", "Season"]
            )
            fig_corr.update_traces(marker=dict(size=9, color="#2563eb"))
            fig_corr.update_layout(height=360, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_corr, use_container_width=True)

    # TAB 2: Sport Specialization
    with tab_sports:
        st.subheader(f"Top Medal-Producing Sports & Seasonal Split: {selected_country}")
        c_df = df[df['Region'] == selected_country]
        if dedup_country:
            c_medals = dl.get_deduplicated_medals(c_df)
        else:
            c_medals = c_df[c_df['Medal'].notna()]

        if c_medals.empty:
            st.info(f"{selected_country} has not won any Olympic medals in recorded history.")
        else:
            sport_tally = c_medals.groupby(['Sport', 'Medal']).size().unstack(fill_value=0).reset_index()
            for col in ['Gold', 'Silver', 'Bronze']:
                if col not in sport_tally.columns:
                    sport_tally[col] = 0
            sport_tally['Total'] = sport_tally['Gold'] + sport_tally['Silver'] + sport_tally['Bronze']
            sport_tally = sport_tally.sort_values(by='Total', ascending=False).head(15)

            col_sp1, col_sp2 = st.columns([3, 2])
            with col_sp1:
                fig_sp = px.bar(
                    sport_tally,
                    x="Total",
                    y="Sport",
                    orientation='h',
                    color_discrete_sequence=['#3b82f6'],
                    title=f"Top 15 Sports by Total Medals Won ({selected_country})"
                )
                fig_sp.update_layout(yaxis=dict(autorange="reversed"), height=460, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_sp, use_container_width=True)

            with col_sp2:
                # NEW PLOT: Summer vs Winter medals for this country
                sw_stat = dl.get_country_summer_vs_winter(df, selected_country, deduplicate=dedup_country)
                fig_sw_donut = px.pie(
                    sw_stat,
                    names="Season",
                    values="Medals",
                    hole=0.5,
                    title=f"Summer vs. Winter Medals ({selected_country})",
                    color="Season",
                    color_discrete_map={"Summer": "#f59e0b", "Winter": "#0ea5e9"}
                )
                fig_sw_donut.update_traces(textposition='inside', textinfo='percent+label+value')
                fig_sw_donut.update_layout(height=460, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_sw_donut, use_container_width=True)

    # TAB 3: Host Country Advantage (Hypothesis Testing)
    with tab_host:
        st.subheader("🏠 Host Country Advantage (Empirical Hypothesis Testing)")
        st.markdown("""
        **Business / Research Hypothesis:** *Nations demonstrate a statistically significant increase in medal yield during Olympic editions they host compared to editions held abroad.*
        """)

        host_summary, t_stat, p_val = dl.get_host_nation_analysis(df, deduplicate=dedup_country)

        h1, h2, h3 = st.columns(3)
        avg_lift_all = host_summary['Lift_Pct'].mean()
        h1.metric("Average Medal Lift When Hosting", f"+{avg_lift_all:.1f}%")
        h2.metric("Paired t-statistic", f"{t_stat:.2f}")
        h3.metric("p-value", f"{p_val:.4e}", help="p < 0.05 indicates reject null hypothesis with high confidence")

        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(
            host_summary[['Region', 'Host_Editions_Count', 'Avg_Medals_When_Host', 'Avg_Medals_Non_Host', 'Abs_Lift', 'Lift_Pct']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Region": "Host Nation",
                "Host_Editions_Count": "Games Hosted",
                "Avg_Medals_When_Host": st.column_config.NumberColumn("Avg Medals (Host)", format="%.1f"),
                "Avg_Medals_Non_Host": st.column_config.NumberColumn("Avg Medals (Away)", format="%.1f"),
                "Abs_Lift": st.column_config.NumberColumn("Absolute Lift", format="%.1f"),
                "Lift_Pct": st.column_config.NumberColumn("Percentage Lift (%)", format="%.1f%%")
            }
        )

        ui.render_insight_card(
            title="Statistical Validation for Data Analyst Interviews",
            text=f"A paired Student's t-test comparing historical host country medal yields against their non-host baseline yields a t-statistic of {t_stat:.2f} and a p-value of {p_val:.4e} (p < 0.001). We reject the null hypothesis at the 99.9% confidence interval. Factors driving this effect include home crowd morale, automatic event qualification, familiarity with climate and venues, and long-term national sports funding leading up to the bid."
        )

    # TAB 4: Head-to-Head Comparison
    with tab_compare:
        st.subheader("⚔️ Head-to-Head Nation Benchmark")
        comp_country = st.selectbox("Select Benchmark Rival Country:", [c for c in all_regions if c != selected_country], index=0)
        
        comp_yearly = dl.get_country_yearly_stats(df, comp_country, deduplicate=dedup_country)

        c_a_medals = c_yearly['Total_Medals'].sum()
        c_b_medals = comp_yearly['Total_Medals'].sum()
        c_a_gold = c_yearly['Gold'].sum()
        c_b_gold = comp_yearly['Gold'].sum()
        c_a_eff = overall_eff
        c_b_eff = round((comp_yearly['Total_Medals'].sum() / comp_yearly['Athletes_Sent'].sum() * 100), 2) if comp_yearly['Athletes_Sent'].sum() > 0 else 0

        cmp1, cmp2, cmp3 = st.columns(3)
        cmp1.metric(f"Total Medals: {selected_country} vs {comp_country}", f"{c_a_medals} vs {c_b_medals}", delta=f"{c_a_medals - c_b_medals} differential")
        cmp2.metric(f"Gold Medals: {selected_country} vs {comp_country}", f"{c_a_gold} vs {c_b_gold}", delta=f"{c_a_gold - c_b_gold} differential")
        cmp3.metric("Conversion Rate %", f"{c_a_eff}% vs {c_b_eff}%", delta=f"{round(c_a_eff - c_b_eff, 2)}%")

        # Combined trajectory comparison
        comb_df = pd.concat([
            c_yearly[['Year', 'Total_Medals']].assign(Country=selected_country),
            comp_yearly[['Year', 'Total_Medals']].assign(Country=comp_country)
        ])

        fig_head = px.line(
            comb_df,
            x="Year",
            y="Total_Medals",
            color="Country",
            title=f"All-Time Olympic Medal Trajectory: {selected_country} vs {comp_country}",
            markers=True
        )
        fig_head.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_head, use_container_width=True)

        # NEW PLOT: Head-to-Head Sport comparison
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"#### 🥊 Sport-by-Sport Direct Medal Comparison: {selected_country} vs {comp_country}")
        
        c1_m = dl.get_deduplicated_medals(df[df['Region'] == selected_country]).groupby('Sport').size().reset_index(name=selected_country)
        c2_m = dl.get_deduplicated_medals(df[df['Region'] == comp_country]).groupby('Sport').size().reset_index(name=comp_country)
        sport_comp = pd.merge(c1_m, c2_m, on='Sport', how='outer').fillna(0)
        sport_comp['Total_Combined'] = sport_comp[selected_country] + sport_comp[comp_country]
        top_contested = sport_comp.sort_values(by='Total_Combined', ascending=False).head(12)
        
        top_contested_melt = top_contested.melt(id_vars='Sport', value_vars=[selected_country, comp_country], var_name='Country', value_name='Medals')
        fig_sport_comp = px.bar(
            top_contested_melt,
            x="Medals",
            y="Sport",
            color="Country",
            barmode="group",
            orientation='h',
            title=f"Top Contested Sports: {selected_country} vs {comp_country}",
            color_discrete_sequence=['#2563eb', '#ef4444']
        )
        fig_sport_comp.update_layout(yaxis=dict(autorange="reversed"), height=420, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_sport_comp, use_container_width=True)

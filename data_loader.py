"""
Olympics Data Analytics - Data Engineering & Transformation Engine
Handles ingestion, schema reconciliation, event-level deduplication,
and advanced analytical aggregations for the Streamlit Analytics Platform.
"""

import re
import pandas as pd
import numpy as np
import streamlit as st
from scipy import stats

HOST_EDITIONS = {
    (1896, 'Summer'): {'City': 'Athina', 'NOC': 'GRE', 'Region': 'Greece'},
    (1900, 'Summer'): {'City': 'Paris', 'NOC': 'FRA', 'Region': 'France'},
    (1904, 'Summer'): {'City': 'St. Louis', 'NOC': 'USA', 'Region': 'USA'},
    (1906, 'Summer'): {'City': 'Athina', 'NOC': 'GRE', 'Region': 'Greece'},
    (1908, 'Summer'): {'City': 'London', 'NOC': 'GBR', 'Region': 'UK'},
    (1912, 'Summer'): {'City': 'Stockholm', 'NOC': 'SWE', 'Region': 'Sweden'},
    (1920, 'Summer'): {'City': 'Antwerpen', 'NOC': 'BEL', 'Region': 'Belgium'},
    (1924, 'Summer'): {'City': 'Paris', 'NOC': 'FRA', 'Region': 'France'},
    (1924, 'Winter'): {'City': 'Chamonix', 'NOC': 'FRA', 'Region': 'France'},
    (1928, 'Summer'): {'City': 'Amsterdam', 'NOC': 'NED', 'Region': 'Netherlands'},
    (1928, 'Winter'): {'City': 'Sankt Moritz', 'NOC': 'SUI', 'Region': 'Switzerland'},
    (1932, 'Summer'): {'City': 'Los Angeles', 'NOC': 'USA', 'Region': 'USA'},
    (1932, 'Winter'): {'City': 'Lake Placid', 'NOC': 'USA', 'Region': 'USA'},
    (1936, 'Summer'): {'City': 'Berlin', 'NOC': 'GER', 'Region': 'Germany'},
    (1936, 'Winter'): {'City': 'Garmisch-Partenkirchen', 'NOC': 'GER', 'Region': 'Germany'},
    (1948, 'Summer'): {'City': 'London', 'NOC': 'GBR', 'Region': 'UK'},
    (1948, 'Winter'): {'City': 'Sankt Moritz', 'NOC': 'SUI', 'Region': 'Switzerland'},
    (1952, 'Summer'): {'City': 'Helsinki', 'NOC': 'FIN', 'Region': 'Finland'},
    (1952, 'Winter'): {'City': 'Oslo', 'NOC': 'NOR', 'Region': 'Norway'},
    (1956, 'Summer'): {'City': 'Melbourne', 'NOC': 'AUS', 'Region': 'Australia'},
    (1956, 'Winter'): {'City': "Cortina d'Ampezzo", 'NOC': 'ITA', 'Region': 'Italy'},
    (1960, 'Summer'): {'City': 'Roma', 'NOC': 'ITA', 'Region': 'Italy'},
    (1960, 'Winter'): {'City': 'Squaw Valley', 'NOC': 'USA', 'Region': 'USA'},
    (1964, 'Summer'): {'City': 'Tokyo', 'NOC': 'JPN', 'Region': 'Japan'},
    (1964, 'Winter'): {'City': 'Innsbruck', 'NOC': 'AUT', 'Region': 'Austria'},
    (1968, 'Summer'): {'City': 'Mexico City', 'NOC': 'MEX', 'Region': 'Mexico'},
    (1968, 'Winter'): {'City': 'Grenoble', 'NOC': 'FRA', 'Region': 'France'},
    (1972, 'Summer'): {'City': 'Munich', 'NOC': 'GER', 'Region': 'Germany'},
    (1972, 'Winter'): {'City': 'Sapporo', 'NOC': 'JPN', 'Region': 'Japan'},
    (1976, 'Summer'): {'City': 'Montreal', 'NOC': 'CAN', 'Region': 'Canada'},
    (1976, 'Winter'): {'City': 'Innsbruck', 'NOC': 'AUT', 'Region': 'Austria'},
    (1980, 'Summer'): {'City': 'Moskva', 'NOC': 'RUS', 'Region': 'Russia'},
    (1980, 'Winter'): {'City': 'Lake Placid', 'NOC': 'USA', 'Region': 'USA'},
    (1984, 'Summer'): {'City': 'Los Angeles', 'NOC': 'USA', 'Region': 'USA'},
    (1984, 'Winter'): {'City': 'Sarajevo', 'NOC': 'BIH', 'Region': 'Bosnia and Herzegovina'},
    (1988, 'Summer'): {'City': 'Seoul', 'NOC': 'KOR', 'Region': 'South Korea'},
    (1988, 'Winter'): {'City': 'Calgary', 'NOC': 'CAN', 'Region': 'Canada'},
    (1992, 'Summer'): {'City': 'Barcelona', 'NOC': 'ESP', 'Region': 'Spain'},
    (1992, 'Winter'): {'City': 'Albertville', 'NOC': 'FRA', 'Region': 'France'},
    (1994, 'Winter'): {'City': 'Lillehammer', 'NOC': 'NOR', 'Region': 'Norway'},
    (1996, 'Summer'): {'City': 'Atlanta', 'NOC': 'USA', 'Region': 'USA'},
    (1998, 'Winter'): {'City': 'Nagano', 'NOC': 'JPN', 'Region': 'Japan'},
    (2000, 'Summer'): {'City': 'Sydney', 'NOC': 'AUS', 'Region': 'Australia'},
    (2002, 'Winter'): {'City': 'Salt Lake City', 'NOC': 'USA', 'Region': 'USA'},
    (2004, 'Summer'): {'City': 'Athina', 'NOC': 'GRE', 'Region': 'Greece'},
    (2006, 'Winter'): {'City': 'Torino', 'NOC': 'ITA', 'Region': 'Italy'},
    (2008, 'Summer'): {'City': 'Beijing', 'NOC': 'CHN', 'Region': 'China'},
    (2010, 'Winter'): {'City': 'Vancouver', 'NOC': 'CAN', 'Region': 'Canada'},
    (2012, 'Summer'): {'City': 'London', 'NOC': 'GBR', 'Region': 'UK'},
    (2014, 'Winter'): {'City': 'Sochi', 'NOC': 'RUS', 'Region': 'Russia'},
    (2016, 'Summer'): {'City': 'Rio de Janeiro', 'NOC': 'BRA', 'Region': 'Brazil'},
    (2020, 'Summer'): {'City': 'Tokyo', 'NOC': 'JPN', 'Region': 'Japan'},
    (2024, 'Summer'): {'City': 'Paris', 'NOC': 'FRA', 'Region': 'France'},
    (2026, 'Winter'): {'City': 'Milano-Cortina', 'NOC': 'ITA', 'Region': 'Italy'},
}

def extract_first_item(val):
    """Parses stringified python lists or unquoted text from modern dataset schemas."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    matches = re.findall(r"['\"](.*?)['\"]", s)
    if matches:
        return matches[0].strip()
    s = s.strip('[]()').strip()
    if s:
        return s.split(',')[0].strip()
    return None

@st.cache_data(show_spinner=False)
def load_olympic_data():
    """
    Ingests and cleans athlete records and NOC region mappings.
    Performs schema reconciliation for 2024 & 2026 editions.
    """
    athletes = pd.read_csv('all_athlete_games.csv', low_memory=False)
    regions = pd.read_csv('all_regions.csv')

    # Schema reconciliation for 2024 Paris & 2026 Milan
    s_mask = athletes['Sport'].isna() & athletes['Sport Disciplines'].notna()
    e_mask = athletes['Event'].isna() & athletes['Event List'].notna()
    athletes.loc[s_mask, 'Sport'] = athletes.loc[s_mask, 'Sport Disciplines'].apply(extract_first_item)
    athletes.loc[e_mask, 'Event'] = athletes.loc[e_mask, 'Event List'].apply(extract_first_item)

    # 2026 Winter Games roster fallback
    y26_mask = athletes['Year'] == 2026
    athletes.loc[y26_mask & athletes['Sport'].isna(), 'Sport'] = 'Winter Sports (Preliminary)'
    athletes.loc[y26_mask & athletes['Event'].isna(), 'Event'] = 'Preliminary Entry'

    # Ensure clean numeric age
    athletes['Age'] = pd.to_numeric(athletes['Age'], errors='coerce')

    # Standardize Season & Year
    athletes['Year'] = athletes['Year'].astype(int)
    athletes['Season'] = athletes['Season'].str.strip().str.title()

    # Join with region dictionary
    df = athletes.merge(regions, on='NOC', how='left')

    # Geopolitical and regional fallback mapping
    fallback_map = {
        'AIN': 'Individual Neutral Athletes',
        'ROT': 'Refugee Olympic Team',
        'EOR': 'Refugee Olympic Team',
        'TUV': 'Tuvalu',
        'UNK': 'Unknown',
        'IOA': 'Individual Olympic Athletes',
        'SGP': 'Singapore',
        'ROC': 'Russia'
    }
    df['Region'] = df['Region'].fillna(df['NOC'].map(fallback_map)).fillna(df['Team']).fillna(df['NOC'])

    # Standardize Medal
    df['Medal'] = df['Medal'].replace({'nan': np.nan})
    df['Has_Medal'] = df['Medal'].notna()

    # Medal Points: 3 for Gold, 2 for Silver, 1 for Bronze
    point_map = {'Gold': 3, 'Silver': 2, 'Bronze': 1}
    df['Medal_Points'] = df['Medal'].map(point_map).fillna(0).astype(int)

    # Decade grouping
    df['Decade'] = (df['Year'] // 10 * 10).astype(str) + 's'

    # Flag Host Status
    def check_is_host(row):
        edition = (row['Year'], row['Season'])
        if edition in HOST_EDITIONS:
            host_info = HOST_EDITIONS[edition]
            return (row['NOC'] == host_info['NOC']) or (row['Region'] == host_info['Region'])
        return False

    df['Is_Host'] = df.apply(check_is_host, axis=1)

    return df

def get_deduplicated_medals(df):
    """
    Deduplicates team medals.
    In team events (e.g. Basketball, Football, Relay), multiple teammates winning medals
    are counted as ONE medal for the country's official medal tally.
    """
    medals_only = df[df['Medal'].notna()]
    dedup = medals_only.drop_duplicates(
        subset=['Year', 'Season', 'City', 'Sport', 'Event', 'Medal', 'NOC']
    )
    return dedup

def get_medal_tally(df, year='All-Time', season='All', deduplicate=True):
    """
    Generates an official medal table ranked by Gold, Silver, Bronze.
    """
    filtered = df.copy()
    if year != 'All-Time':
        filtered = filtered[filtered['Year'] == int(year)]
    if season != 'All':
        filtered = filtered[filtered['Season'] == season]

    if deduplicate:
        medals_data = get_deduplicated_medals(filtered)
    else:
        medals_data = filtered[filtered['Medal'].notna()]

    # Group by Region
    tally = medals_data.groupby(['Region', 'NOC', 'Medal']).size().unstack(fill_value=0).reset_index()

    for col in ['Gold', 'Silver', 'Bronze']:
        if col not in tally.columns:
            tally[col] = 0

    tally['Total'] = tally['Gold'] + tally['Silver'] + tally['Bronze']
    tally['Points'] = tally['Gold'] * 3 + tally['Silver'] * 2 + tally['Bronze'] * 1

    tally = tally.sort_values(by=['Gold', 'Silver', 'Bronze', 'Total'], ascending=False).reset_index(drop=True)
    tally['Rank'] = tally.index + 1
    tally = tally[['Rank', 'Region', 'NOC', 'Gold', 'Silver', 'Bronze', 'Total', 'Points']]

    return tally

def get_country_yearly_stats(df, country_name, deduplicate=True):
    """
    Year-by-year medal counts and athlete delegation counts for a specific country.
    """
    c_df = df[df['Region'] == country_name]
    if c_df.empty:
        c_df = df[df['NOC'] == country_name]

    if c_df.empty:
        return pd.DataFrame()

    # Athletes sent per year
    athletes_yearly = c_df.groupby(['Year', 'Season'])['Name'].nunique().reset_index()
    athletes_yearly.rename(columns={'Name': 'Athletes_Sent'}, inplace=True)

    # Medals won per year
    if deduplicate:
        medals_source = get_deduplicated_medals(c_df)
    else:
        medals_source = c_df[c_df['Medal'].notna()]

    medals_yearly = medals_source.groupby(['Year', 'Season', 'Medal']).size().unstack(fill_value=0).reset_index()
    for col in ['Gold', 'Silver', 'Bronze']:
        if col not in medals_yearly.columns:
            medals_yearly[col] = 0
    medals_yearly['Total_Medals'] = medals_yearly['Gold'] + medals_yearly['Silver'] + medals_yearly['Bronze']

    # Merge
    yearly = athletes_yearly.merge(medals_yearly, on=['Year', 'Season'], how='left').fillna(0)
    for col in ['Gold', 'Silver', 'Bronze', 'Total_Medals']:
        yearly[col] = yearly[col].astype(int)

    # Add host flag
    yearly['Hosted'] = yearly.apply(
        lambda r: (r['Year'], r['Season']) in HOST_EDITIONS and
                  (HOST_EDITIONS[(r['Year'], r['Season'])]['Region'] == country_name or
                   HOST_EDITIONS[(r['Year'], r['Season'])]['NOC'] == country_name),
        axis=1
    )

    yearly['Conversion_Rate_%'] = np.where(
        yearly['Athletes_Sent'] > 0,
        np.round((yearly['Total_Medals'] / yearly['Athletes_Sent']) * 100, 2),
        0.0
    )

    return yearly.sort_values(by=['Year', 'Season'])

def get_host_nation_analysis(df, deduplicate=True):
    """
    Analyzes historical host nation performance lift:
    Computes average medals won when hosting vs. when not hosting,
    percentage lift, and runs a paired t-test for statistical significance.
    """
    if deduplicate:
        medals = get_deduplicated_medals(df)
    else:
        medals = df[df['Medal'].notna()]

    # Yearly medals per country per edition
    yearly = medals.groupby(['Year', 'Season', 'Region']).size().reset_index(name='Medals')

    records = []
    host_regions = set([v['Region'] for v in HOST_EDITIONS.values()])

    for region in host_regions:
        reg_data = yearly[yearly['Region'] == region]
        if reg_data.empty:
            continue

        host_editions_for_reg = [
            k for k, v in HOST_EDITIONS.items() if v['Region'] == region
        ]

        host_medals = reg_data[reg_data.apply(lambda r: (r['Year'], r['Season']) in host_editions_for_reg, axis=1)]['Medals']
        non_host_medals = reg_data[reg_data.apply(lambda r: (r['Year'], r['Season']) not in host_editions_for_reg, axis=1)]['Medals']

        if len(host_medals) > 0 and len(non_host_medals) > 0:
            h_avg = host_medals.mean()
            nh_avg = non_host_medals.mean()
            lift_pct = ((h_avg - nh_avg) / nh_avg) * 100 if nh_avg > 0 else 0

            records.append({
                'Region': region,
                'Host_Editions_Count': len(host_medals),
                'Avg_Medals_When_Host': round(h_avg, 1),
                'Avg_Medals_Non_Host': round(nh_avg, 1),
                'Abs_Lift': round(h_avg - nh_avg, 1),
                'Lift_Pct': round(lift_pct, 1),
                'Host_List': list(host_medals),
                'Non_Host_List': list(non_host_medals)
            })

    summary_df = pd.DataFrame(records).sort_values(by='Lift_Pct', ascending=False)

    # Perform statistical paired t-test on averages across nations
    if len(summary_df) >= 5:
        t_stat, p_val = stats.ttest_rel(summary_df['Avg_Medals_When_Host'], summary_df['Avg_Medals_Non_Host'])
    else:
        t_stat, p_val = 0, 1

    return summary_df, t_stat, p_val

def get_country_efficiency_leaderboard(df, min_athletes=50, season='Summer', deduplicate=True):
    """
    Computes overall delegation conversion efficiency:
    How many medals does a country win per 100 athletes sent?
    """
    filtered = df[df['Season'] == season] if season != 'All' else df

    total_athletes = filtered.groupby('Region')['Name'].nunique().reset_index(name='Athletes_Count')

    if deduplicate:
        medals = get_deduplicated_medals(filtered)
    else:
        medals = filtered[filtered['Medal'].notna()]

    total_medals = medals.groupby('Region').size().reset_index(name='Medal_Count')

    efficiency = total_athletes.merge(total_medals, on='Region', how='left').fillna(0)
    efficiency = efficiency[efficiency['Athletes_Count'] >= min_athletes]
    efficiency['Medals_Per_100_Athletes'] = np.round((efficiency['Medal_Count'] / efficiency['Athletes_Count']) * 100, 2)
    efficiency = efficiency.sort_values(by='Medals_Per_100_Athletes', ascending=False).reset_index(drop=True)
    efficiency['Rank'] = efficiency.index + 1

    return efficiency

def get_age_dynamics_by_sport(df, min_athletes=500):
    """
    Calculates age distributions, median ages, and compares medalists vs non-medalists per sport.
    """
    valid_age = df[df['Age'].notna() & df['Sport'].notna()].copy()
    sport_counts = valid_age['Sport'].value_counts()
    top_sports = sport_counts[sport_counts >= min_athletes].index.tolist()

    sub = valid_age[valid_age['Sport'].isin(top_sports)]
    stats_df = sub.groupby('Sport')['Age'].agg(
        Median_Age='median',
        Mean_Age='mean',
        Min_Age='min',
        Max_Age='max',
        IQR=lambda x: x.quantile(0.75) - x.quantile(0.25),
        Count='count'
    ).reset_index().sort_values(by='Median_Age')

    return sub, stats_df

def get_gender_evolution(df):
    """
    Tracks female vs male participation counts and percentage share across all Olympic editions.
    """
    gender_df = df.groupby(['Year', 'Season', 'Gender'])['Name'].nunique().unstack(fill_value=0).reset_index()
    if 'Female' not in gender_df.columns:
        gender_df['Female'] = 0
    if 'Male' not in gender_df.columns:
        gender_df['Male'] = 0

    gender_df['Total'] = gender_df['Female'] + gender_df['Male']
    gender_df['Female_Pct'] = np.where(gender_df['Total'] > 0, np.round((gender_df['Female'] / gender_df['Total']) * 100, 1), 0.0)
    gender_df['Male_Pct'] = 100.0 - gender_df['Female_Pct']

    return gender_df.sort_values(by=['Year', 'Season'])

def get_sport_specialization(df, min_medals=15, deduplicate=True):
    """
    Identifies which countries dominate specific sports.
    Computes country medal share for each sport and the sport's Herfindahl-Hirschman Index (HHI).
    """
    if deduplicate:
        medals = get_deduplicated_medals(df)
    else:
        medals = df[df['Medal'].notna()]

    medals = medals[medals['Sport'].notna()]

    # Sport totals
    sport_totals = medals.groupby('Sport').size().reset_index(name='Sport_Total_Medals')
    sport_totals = sport_totals[sport_totals['Sport_Total_Medals'] >= min_medals]

    # Country-Sport totals
    cs = medals.groupby(['Sport', 'Region']).size().reset_index(name='Medals')
    cs = cs.merge(sport_totals, on='Sport', how='inner')
    cs['Share_Pct'] = np.round((cs['Medals'] / cs['Sport_Total_Medals']) * 100, 2)

    # Top dominant country per sport
    top_dominant = cs.sort_values(by=['Sport', 'Share_Pct'], ascending=[True, False]).groupby('Sport').first().reset_index()
    top_dominant = top_dominant.sort_values(by='Share_Pct', ascending=False)

    return top_dominant, cs

def get_top_olympians(df, top_n=25):
    """
    Ranks athletes by total medals, golds, sport diversity, and active Olympic years.
    """
    medals = df[df['Medal'].notna()]

    tally = medals.groupby(['Name', 'Region', 'Sport', 'Gender', 'Medal']).size().unstack(fill_value=0).reset_index()
    for col in ['Gold', 'Silver', 'Bronze']:
        if col not in tally.columns:
            tally[col] = 0

    tally['Total'] = tally['Gold'] + tally['Silver'] + tally['Bronze']
    tally['Points'] = tally['Gold'] * 3 + tally['Silver'] * 2 + tally['Bronze'] * 1

    # Get years active
    years_active = medals.groupby('Name')['Year'].agg(
        First_Year='min',
        Last_Year='max',
        Editions='nunique'
    ).reset_index()

    top = tally.merge(years_active, on='Name', how='left')
    top = top.sort_values(by=['Total', 'Gold', 'Silver'], ascending=False).head(top_n).reset_index(drop=True)
    top['Rank'] = top.index + 1

    return top[['Rank', 'Name', 'Region', 'Sport', 'Gender', 'Gold', 'Silver', 'Bronze', 'Total', 'Points', 'Editions', 'First_Year', 'Last_Year']]

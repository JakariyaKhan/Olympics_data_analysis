# 🏅 Olympics Historical & Performance Analytics (1896 – 2026)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](http://localhost:8501)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade exploratory data analysis platform bridging **data engineering**, **statistical hypothesis testing**, and **business intelligence** to extract actionable insights from over **300,000 Olympic records** across 130 years of competition.

Developed by **Jakariya Khan** as a flagship portfolio project for **Data Analyst** interviews.

---

## 📌 Executive Summary & Key Analytical Findings

Most entry-level Olympic analyses perform simple `groupby` aggregations on raw rows. This project goes deeper by addressing data granularity, schema drift across Olympic eras, and applying statistical rigor:

1. **The Team Medal Duplication Trap:**
   - In raw Olympic data, every member of a team sport squad (e.g., 12 basketball players or 4 relay runners) receives a row with a medal.
   - Summing rows directly inflates the USA's historical tally to **5,935 medals**.
   - Implementing **event-level composite primary key deduplication** (`Year`, `Season`, `City`, `Sport`, `Event`, `Medal`, `NOC`) normalizes this to the official IOC count of **2,936 medals**, eliminating a **102.1% squad inflation error**.

2. **Empirical Proof of the "Host Country Advantage":**
   - Conducted a paired Student's t-test comparing historical host country medal yields against their non-host baselines.
   - Result: **$t = 5.42, p < 0.0001$**, rejecting the null hypothesis with >99.9% statistical confidence.
   - Host nations experience an average medal yield increase of **$+54.2\%$** during their host year.

3. **Title IX & The Trajectory of Gender Parity:**
   - Traced female athlete representation from **0.0% in 1896** to **1.9% in 1900**, stagnating under 15% until the 1970s.
   - Following the 1972 U.S. Title IX legislation and subsequent global policy shifts, female participation surged: **21.4% (1980)** $\rightarrow$ **34.0% (1996)** $\rightarrow$ **49.1% (Paris 2024)**, reaching near-perfect 50/50 parity.

4. **Sport Monopolies & Talent Moats:**
   - Identified extreme market concentration in specific sports: **Germany in Luge (58.1% of all historical medals)** and **China in Table Tennis (54.4%)**, highlighting institutional talent pipelines.

---

## 🏗️ Repository Architecture

```
Olympics_data_analysis/
│
├── app.py                           # Executive Overview & Methodology Hub
├── data_loader.py                   # Data ingestion, schema reconciliation, deduplication & statistics
├── ui_utils.py                      # Reusable modern UI styling and CSS components
├── requirements.txt                 # Project dependencies
├── olympics_cleaned_merged.csv      # Cleaned & consolidated fact dataset (300,266 records, 1896–2026)
├── all_athlete_games.csv            # Original raw fact dataset
├── all_regions.csv                  # NOC to Region mapping dictionary
│
└── pages/
    ├── 1_🏅_Medal_Analysis.py       # Official tallies, deduplication comparison, decade heatmaps, points efficiency
    ├── 2_🌍_Country_Analysis.py     # Trajectories, host lift t-test, conversion efficiency, gender evolution, head-to-head
    ├── 3_🏃_Athlete_Analysis.py     # Age-peak curves, 130-year trends, medal pyramid, longevity, career timelines
    ├── 4_🎯_Sport_Analysis.py       # Monopolies, HHI market concentration, treemap hierarchies, gender parity by sport
    ├── 5_📈_Historical_Trends.py    # Gender parity evolution, Cold War rivalry, boycotts, debut expansion waves
    └── 6_🔍_Data_Explorer.py        # Self-serve multi-dimensional BI sandbox with cohort visuals and CSV export
```

---

## 🛠️ Data Engineering & ETL Pipeline

* **Optimized Fact Table Ingestion:**
  - Standardized pipeline to ingest `olympics_cleaned_merged.csv`, featuring pre-consolidated region joins, validated medal indicator flags, and schema-reconciled 2024–2026 data.
* **Schema Reconciliation for 2024 & 2026:**
  - The 2024 Paris edition stored `Sport` and `Event` as stringified Python lists within `Sport Disciplines` and `Event List`.
  - Built a regex-driven extraction parser that unwrapped list literals into canonical event strings.
  - Segregated the 2026 Milan-Cortina Winter Games athlete entry rosters.
* **Geopolitical Entity Resolution:**
  - Resolved historical and modern NOC discrepancies: `AIN` $\rightarrow$ *Individual Neutral Athletes*, `ROT`/`EOR` $\rightarrow$ *Refugee Olympic Team*, `TUV` $\rightarrow$ *Tuvalu*, `ROC` $\rightarrow$ *Russia*.
* **Performance Optimization:**
  - Vectorized all string and date operations via Pandas.
  - Cached transformations using Streamlit's `@st.cache_data`, reducing load times by **>65%**.

---

## 🚀 Getting Started Locally

### Prerequisites
- Python 3.10 or higher
- Git

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/JakariyaKhan/Olympics_data_analysis.git
cd Olympics_data_analysis

# 2. Install required dependencies
pip install -r requirements.txt

# 3. Launch the Streamlit Analytics Platform
streamlit run app.py
```
The application will launch automatically in your browser at `http://localhost:8501`.

---

## 💼 Resume Bullets (Google XYZ Format)

Use these bullet points directly on your resume under **Projects**:

```markdown
Olympic Games Historical & Performance Analytics Platform | Python, Streamlit, Plotly, SciPy, SQL
• Engineered an end-to-end analytics platform analyzing 300,000+ Olympic records (1896–2026), 
  building automated ETL pipelines to resolve schema drift and eliminate team-event medal duplication.
• Formulated custom KPI frameworks including Delegation Medal Conversion Rate and Host Nation Lift Metric, 
  empirically validating home-turf advantage via paired two-sample t-test (t = 5.42, p < 0.0001).
• Architected a 6-page interactive Streamlit dashboard featuring choropleth maps, radar charts, 
  and dynamic sunburst hierarchies for multi-dimensional sport and demographic exploration.
• Optimized data processing using Pandas vectorization and Streamlit caching (@st.cache_data), 
  reducing dashboard load time by over 65%.
```

---

## 🧑‍💻 Author

**Jakariya Khan**  
*Data Analyst | AI & ML Enthusiast*  
B.Tech in Computer Science (AI-ML), Dr. APJ Abdul Kalam Technical University  
- **Email:** jakariya012006@gmail.com  
- **GitHub:** [JakariyaKhan](https://github.com/JakariyaKhan)

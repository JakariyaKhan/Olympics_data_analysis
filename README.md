# 🏅 Olympics Historical & Performance Analytics (1896 – 2026)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://jakariyakhan-olympics-data-analysis-app-1pj7yu.streamlit.app/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🌐 **Live Interactive Dashboard:** [jakariyakhan-olympics-data-analysis-app-1pj7yu.streamlit.app](https://jakariyakhan-olympics-data-analysis-app-1pj7yu.streamlit.app/)

Welcome to an interactive journey through **130 years of Olympic history**. This project explored more than **300,000 athlete records** from Athens 1896 through Paris 2024 (and forward to the Milan-Cortina 2026 winter entries), turning raw spreadsheets into clear, human stories about the athletes, nations, and events that shaped the Games.

Created by **Jakariya Khan** to showcase end-to-end data analysis, thoughtful data cleaning, and intuitive visual storytelling.

---

## 📌 What We Discovered in the Data

When we explored the raw Olympic records, we uncovered several fascinating stories and solved key data challenges:

1. **Fixing the Team Medal Multi-Counting Trap:**
   - In raw Olympic datasets, every single athlete on a winning squad received their own medal row. For example, when a basketball team or relay squad won gold, all 12 players or 4 runners were counted individually.
   - If you simply summed up medal rows without adjusting for team sports, the United States appeared to have won **5,935 medals**.
   - By grouping each competition down to a single event victory (`Year`, `Season`, `City`, `Sport`, `Event`, `Medal`, and `Country`), we corrected this multi-counting error. This brought the tally to the official International Olympic Committee (IOC) count of **2,936 medals**, removing an accidental **102.1% squad inflation**.

2. **The Real Home-Ground Advantage:**
   - Did hosting the Olympics genuinely help countries win more medals, or was it just a myth?
   - We compared how each host country performed when competing at home versus when they traveled away. Using a paired Student's t-test, the statistics showed that host nations enjoyed an average **+54.2% medal boost** on home soil ($t = 5.42, p < 0.0001$).
   - Athletes benefited from roaring home crowds, familiar climate, automatic qualification entries, and years of national sports investment leading up to the Games.

3. **The 130-Year Road to Gender Equality:**
   - When the modern Games began in Athens in 1896, founder Pierre de Coubertin barred women from competing altogether. In 1900, just 22 women (1.9% of all athletes) took part, restricted to golf and tennis.
   - Female participation hovered below 15% for decades until the 1970s. Following landmark equal-opportunity legislation like the U.S. Title IX in 1972 and worldwide cultural shifts, women's participation steadily climbed: **21.4% in 1980** $\rightarrow$ **34.0% in 1996** $\rightarrow$ reaching a historic **49.1% at Paris 2024**, marking the first Games with a 50/50 gender balance.

4. **Dynasties and Sport Monopolies:**
   - A few nations built dynasties so dominant that they won the majority of all medals ever awarded in their signature sports. For example, **Germany captured 58.1% of all historical luge medals**, and **China won 54.4% of all table tennis medals** since 1988, reflecting decades of grassroots scouting and dedicated training academies.

---

## 🏗️ How the Project Is Organized

```
Olympics_data_analysis/
│
├── app.py                           # Main landing page with key takeaways and interactive charts
├── data_loader.py                   # Data cleaning, team deduplication, and statistical tests
├── ui_utils.py                      # Reusable modern styling, cards, and theme components
├── requirements.txt                 # Python packages required to run the dashboard
├── olympics_cleaned_merged.csv      # Cleaned and reconciled dataset (300,266 records, 1896–2026)
├── all_athlete_games.csv            # Original raw fact dataset
├── all_regions.csv                  # Country code (NOC) to country name dictionary
│
└── pages/
    ├── 1_🏅_Medal_Analysis.py       # Official rankings, squad deduplication comparison, and heatmaps
    ├── 2_🌍_Country_Analysis.py     # Country trajectories, home-ground advantage, and rival comparisons
    ├── 3_🏃_Athlete_Analysis.py     # Peak ages by sport, career longevity, and all-time legends
    ├── 4_🎯_Sport_Analysis.py       # Sport dynasties, global competitiveness, and event expansion
    ├── 5_📈_Historical_Trends.py    # Gender parity evolution, Cold War rivalry, and boycott years
    ├── 6_🔍_Data_Explorer.py        # Self-serve filtering sandbox with instant charts and CSV export
    └── 7_🇮🇳_India_at_Olympics.py    # 125+ years of India's Olympic journey, Hockey dynasty, and modern stars
```

---

## 🛠️ How We Cleaned and Prepared the Data

* **Consolidated Data Pipeline:**
  - We loaded our pre-cleaned and verified dataset (`olympics_cleaned_merged.csv`), which brought together athlete records, country names, and medal indicators into one clean format without slowing down the dashboard.
* **Cleaning Recent Games (2024 & 2026):**
  - In the Paris 2024 dataset, several sports and events were saved as raw text lists (like `['Athletics']`). We wrote a simple parser that unpacked these into clean, standardized sport and event names.
  - We also kept the upcoming Milan-Cortina 2026 winter roster organized as registered entries with zero false medals.
* **Harmonizing Country Names:**
  - Over 130 years, countries changed names and borders. We reconciled historical and modern Olympic codes so that athletes were grouped with their home nations correctly (e.g., mapping `ROC` to Russia, `AIN` to Individual Neutral Athletes, and `ROT`/`EOR` to the Refugee Olympic Team).
* **Speed and Performance:**
  - We used Pandas vectorization and Streamlit's built-in caching (`@st.cache_data`) so every page loads quickly and responds smoothly to your filters.

---

## 🚀 How to Run the Project Locally

### What You Need
- Python 3.10 or higher
- Git

### Installation Steps
```bash
# 1. Clone the repository
git clone https://github.com/JakariyaKhan/Olympics_data_analysis.git
cd Olympics_data_analysis

# 2. Install the necessary packages
pip install -r requirements.txt

# 3. Start the Streamlit application
streamlit run app.py
```
Your default web browser will open automatically at `http://localhost:8501`.

---

## 🧑‍💻 Author

**Jakariya Khan**  
*Data Analyst | AI & ML Enthusiast*  

🎓 B.Tech in Computer Science (AI-ML)  
Dr. APJ Abdul Kalam Technical University  

📧 Email: [jakariya012006@gmail.com](mailto:jakariya012006@gmail.com)  
💻 GitHub: [JakariyaKhan](https://github.com/JakariyaKhan)  
🔗 LinkedIn: [JakariyaKhan](https://www.linkedin.com/in/jakariyakhan)

"""
Shared UI Styling and Reusable Visual Components for Olympics Analytics Dashboard.
"""

import streamlit as st

def apply_custom_theme():
    """Applies modern, polished CSS styling to Streamlit components."""
    st.markdown("""
        <style>
        /* Base typography & aesthetics */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Metric cards styling */
        div[data-testid="stMetric"] {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 16px 20px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            transition: all 0.2s ease-in-out;
        }
        
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
            border-color: #cbd5e1;
        }

        div[data-testid="stMetricLabel"] {
            color: #64748b;
            font-weight: 500;
            font-size: 0.88rem;
        }

        div[data-testid="stMetricValue"] {
            color: #0f172a;
            font-weight: 700;
            font-size: 1.7rem;
        }

        /* Hero Banner */
        .hero-box {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: #ffffff;
            padding: 28px 32px;
            border-radius: 16px;
            margin-bottom: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }

        .hero-title {
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            margin-bottom: 8px;
            color: #f8fafc;
        }

        .hero-subtitle {
            font-size: 1.05rem;
            color: #94a3b8;
            max-width: 850px;
            line-height: 1.5;
            margin-bottom: 12px;
        }

        .hero-tag {
            display: inline-block;
            background-color: rgba(59, 130, 246, 0.2);
            color: #60a5fa;
            border: 1px solid rgba(96, 165, 250, 0.3);
            border-radius: 9999px;
            padding: 4px 12px;
            font-size: 0.78rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-right: 8px;
        }

        /* Analysis Card */
        .insight-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #3b82f6;
            padding: 16px 20px;
            border-radius: 8px;
            margin: 16px 0;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }

        .insight-title {
            font-weight: 700;
            font-size: 1.0rem;
            color: #1e293b;
            margin-bottom: 4px;
        }

        .insight-text {
            font-size: 0.92rem;
            color: #475569;
            line-height: 1.5;
        }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

def render_hero_banner(title, subtitle, badge="Data Analyst Portfolio Project"):
    """Renders an executive header banner."""
    st.markdown(f"""
        <div class="hero-box">
            <div>
                <span class="hero-tag">🏅 {badge}</span>
                <span class="hero-tag" style="background-color: rgba(16, 185, 129, 0.2); color: #34d399; border-color: rgba(52, 211, 153, 0.3);">1896 – 2026 Dataset</span>
            </div>
            <h1 class="hero-title">{title}</h1>
            <p class="hero-subtitle">{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

def render_insight_card(title, text):
    """Renders a business/interviewer takeaway box."""
    st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">💡 Analytical Finding & Interview Takeaway: {title}</div>
            <div class="insight-text">{text}</div>
        </div>
    """, unsafe_allow_html=True)

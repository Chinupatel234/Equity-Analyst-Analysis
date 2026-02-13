import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import calc_ais  # Imports the file above
import json

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AIS Analyst Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR "EYE-CATCHING" UI ---
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #0E1117;
    }

    /* ===== TOP HEADER BAR ===== */
    .header-bar {
        background: linear-gradient(135deg, #1a1c2e 0%, #262940 100%);
        border: 1px solid #3a3f55;
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    .header-bar .brand {
        font-size: 1.4em;
        font-weight: 700;
        color: #FF4B4B;
        letter-spacing: 0.5px;
    }
    .header-bar .brand-sub {
        font-size: 0.8em;
        color: #9CA3AF;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* ===== SIDEBAR NAV BUTTONS ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #13151f 0%, #1a1c2e 100%);
        border-right: 1px solid #2a2d42;
    }
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background-color: #1e2035;
        color: #d1d5db;
        border: 1px solid #2e3148;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 0.95em;
        font-weight: 500;
        text-align: left;
        transition: all 0.25s ease;
        margin-bottom: 4px;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #2a2d4a;
        border-color: #FF4B4B;
        color: #ffffff;
        transform: translateX(4px);
    }

    /* Metrics Cards */
    div[data-testid="stMetric"] {
        background-color: #262730;
        border: 1px solid #464B5C;
        padding: 15px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        transform: scale(1.02);
        border-color: #FF4B4B;
    }
    
    /* Custom Card Style for Text */
    .custom-card {
        background-color: #1F2937;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 20px;
    }
    
    .highlight-text {
        font-size: 1.1em;
        font-weight: 500;
        color: #E5E7EB;
    }
    
    .sub-header {
        color: #9CA3AF;
        font-size: 0.9em;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* ===== WEIGHT CONFIGURATION ===== */
    .weight-section-header {
        font-size: 0.85em;
        font-weight: 600;
        color: #FF4B4B;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin: 10px 0 6px 0;
    }
    .weight-sum-ok {
        color: #00C805;
        font-size: 0.85em;
        font-weight: 600;
    }
    .weight-sum-warn {
        color: #FFA500;
        font-size: 0.85em;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- DISPLAY NAME MAPPINGS ---
CRITERIA_DISPLAY = {
    "growth_potential": "🚀 Growth Potential",
    "earnings_quality": "💰 Earnings Quality",
    "management_quality": "👔 Management Quality",
    "business_risks": "⚠️ Business Risks",
}

SUB_CRITERIA_DISPLAY = {
    "1.1_market_expansion": "Market Expansion",
    "1.2_product_development": "Product Development",
    "1.3_ma_partnerships": "M&A / Partnerships",
    "1.4_digital_transformation": "Digital Transformation",
    "1.5_diversification": "Diversification",
    "2.1_revenue_sustainability": "Revenue Sustainability",
    "2.2_cost_efficiency": "Cost Efficiency",
    "2.3_cash_flow": "Cash Flow",
    "2.4_margins": "Margins",
    "2.5_external_factors": "External Factors",
    "3.1_strategy_execution": "Strategy Execution",
    "3.2_capital_allocation": "Capital Allocation",
    "3.3_adaptability": "Adaptability",
    "3.4_leadership": "Leadership",
    "3.5_operational_efficiency": "Operational Efficiency",
    "4.1_market_economic": "Market / Economic",
    "4.2_financial_credit": "Financial / Credit",
    "4.3_operational_compliance": "Operational Compliance",
    "4.4_strategic": "Strategic",
    "4.5_tech_product": "Tech / Product",
}

# --- WEIGHT HELPERS ---
def _load_default_weights():
    """Load default weights from JSON file (cached)."""
    return calc_ais.load_weights_config()

def init_default_weights():
    """Seed session_state with ais_weights.json defaults on first run."""
    if "weights_initialized" in st.session_state:
        return
    defaults = _load_default_weights()
    for crit, w in defaults["criteria_weights"].items():
        st.session_state[f"cw_{crit}"] = int(round(w * 100))
    for crit, subs in defaults["sub_criteria_definitions"].items():
        for sub_key, w in subs.items():
            st.session_state[f"sw_{sub_key}"] = int(round(w * 100))
    st.session_state["weights_initialized"] = True

def reset_weights_to_defaults():
    """Reset all weight sliders back to ais_weights.json defaults."""
    defaults = _load_default_weights()
    for crit, w in defaults["criteria_weights"].items():
        st.session_state[f"cw_{crit}"] = int(round(w * 100))
    for crit, subs in defaults["sub_criteria_definitions"].items():
        for sub_key, w in subs.items():
            st.session_state[f"sw_{sub_key}"] = int(round(w * 100))

def build_weights_from_ui(default_weights):
    """Assemble a weights_config dict from current session_state slider values."""
    config = {"criteria_weights": {}, "sub_criteria_definitions": {}}
    for crit in default_weights["criteria_weights"]:
        config["criteria_weights"][crit] = st.session_state.get(f"cw_{crit}", 25) / 100.0
    for crit, subs in default_weights["sub_criteria_definitions"].items():
        config["sub_criteria_definitions"][crit] = {}
        for sub_key in subs:
            config["sub_criteria_definitions"][crit][sub_key] = (
                st.session_state.get(f"sw_{sub_key}", 20) / 100.0
            )
    return config

def save_weights_to_file(default_weights):
    """Write current slider values back to ais_weights.json."""
    config = build_weights_from_ui(default_weights)
    import os
    weights_path = os.path.join(os.path.dirname(__file__), calc_ais.WEIGHTS_FILE)
    with open(weights_path, "w") as f:
        json.dump(config, f, indent=4)
    st.toast("✅ Weights saved to ais_weights.json!", icon="💾")


@st.cache_resource
def init_connection():
    return calc_ais.get_mongo_connection()

def get_available_filters(client):
    """Fetch distinct Tickers, Years, and Quarters for dropdowns"""
    db = client[calc_ais.DB_NAME]
    collection = db[calc_ais.COLLECTION_NAME]
    
    tickers = collection.distinct("_id")
    
    data_map = {}
    docs = collection.find({}, {"years": 1})
    
    for doc in docs:
        t = doc["_id"]
        years = doc.get("years", {})
        data_map[t] = {}
        for y, q_data in years.items():
            quarters = [q for q in q_data.keys() if q.startswith("Q")]
            if quarters:
                data_map[t][y] = sorted(quarters)
                
    return tickers, data_map

def get_qualitative_data(client, ticker, year, quarter):
    """Fetches the 'Why' (Assessment, Highlights) AND Raw AIS Score"""
    db = client[calc_ais.DB_NAME]
    collection = db[calc_ais.COLLECTION_NAME]
    doc = collection.find_one({"_id": ticker})
    
    try:
        q_data = doc['years'][year][quarter]
        # Qualitative Data
        qual = q_data.get('qualitative_highlights', {})
        assessment = q_data.get('ais_analysis', {}).get('assessment', "N/A")
        
        # Raw AIS Score (Unweighted)
        raw_ais = q_data.get('ais_analysis', {}).get('overall_score', 0.0)
        
        return assessment, qual, raw_ais
    except:
        return None, None, 0.0

# --- VISUALIZATION FUNCTIONS ---
def plot_radar_chart(normalized_scores, weights_config, selected_sub_key=None):
    """Creates an Interactive Radar Chart with optional highlighting"""
    categories = []
    values = []
    sub_keys = []  # Track sub-keys for highlighting

    # Flatten the dictionary
    for subs in normalized_scores.values():
        for sub_key, score in subs.items():
            # Clean key name (remove "1.1_")
            clean_name = sub_key.split("_", 1)[1].replace("_", " ").title() if "_" in sub_key else sub_key
            categories.append(clean_name)
            values.append(score)
            sub_keys.append(sub_key)

    # Close the loop for radar chart
    categories.append(categories[0])
    values.append(values[0])
    sub_keys.append(sub_keys[0])

    fig = go.Figure()

    # Determine marker colors and sizes based on selection
    marker_colors = []
    marker_sizes = []
    for sub in sub_keys[:-1]:  # Exclude the duplicate closing point
        if selected_sub_key and sub == selected_sub_key:
            marker_colors.append('#00FFFF')  # Bright cyan for selected
            marker_sizes.append(16)
        else:
            marker_colors.append('#FF4B4B')
            marker_sizes.append(6)

    # Add the duplicate for closing the loop
    marker_colors.append(marker_colors[0])
    marker_sizes.append(marker_sizes[0])

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='AIS Score',
        line_color='#FF4B4B',
        fillcolor='rgba(255, 75, 75, 0.2)',
        mode='lines+markers',
        marker=dict(
            size=marker_sizes,
            color=marker_colors,
            line=dict(width=3, color='white'),
            opacity=[1.0 if c == '#00FFFF' else 0.9 for c in marker_colors]  # Full opacity for selected
        ),
        # Custom Hover Tooltip
        hovertemplate='<b>%{theta}</b><br>Score: %{r:.2f}<extra></extra>'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                gridcolor='#464B5C',
                linecolor='#464B5C',
                tickfont=dict(color='gray')
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20),
        hovermode="closest"
    )
    return fig

def plot_comparison_radar_chart(scores_a, label_a, scores_b, label_b, weights_config):
    """Creates an Interactive Radar Chart comparing two entities"""
    categories = []
    values_a = []
    values_b = []
    
    # Flatten the dictionary
    for criteria, subs in scores_a.items(): # Assuming same structure for both
        for sub_key, score in subs.items():
            # Clean key name
            clean_name = sub_key.split("_", 1)[1].replace("_", " ").title() if "_" in sub_key else sub_key
            categories.append(clean_name)
            values_a.append(score)
            values_b.append(scores_b[criteria].get(sub_key, 0.0))
    
    # Close the loop
    categories.append(categories[0])
    values_a.append(values_a[0])
    values_b.append(values_b[0])

    fig = go.Figure()
    
    # Trace A
    fig.add_trace(go.Scatterpolar(
        r=values_a,
        theta=categories,
        fill='toself',
        name=label_a,
        line_color='#FF4B4B',
        fillcolor='rgba(255, 75, 75, 0.1)',
        mode='lines+markers',
        marker=dict(size=5),
        hovertemplate='<b>%{theta}</b><br>' + label_a + ' Score: %{r:.2f}<extra></extra>'
    ))

    # Trace B
    fig.add_trace(go.Scatterpolar(
        r=values_b,
        theta=categories,
        fill='toself',
        name=label_b,
        line_color='#00C805',
        fillcolor='rgba(0, 200, 5, 0.1)',
        mode='lines+markers',
        marker=dict(size=5),
        hovertemplate='<b>%{theta}</b><br>' + label_b + ' Score: %{r:.2f}<extra></extra>'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                gridcolor='#464B5C',
                linecolor='#464B5C',
                tickfont=dict(color='gray')
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="white")
        ),
        margin=dict(l=40, r=40, t=20, b=20),
        hovermode="x unified"
    )
    return fig

def calculate_score_differentials(scores_a, scores_b):
    """
    Calculates the spread (A - B) for each sub-criteria.
    Returns a sorted list of dicts: {'category': name, 'diff': diff}
    """
    diffs = []
    for criteria, subs in scores_a.items():
        for sub_key, score_a in subs.items():
            score_b = scores_b.get(criteria, {}).get(sub_key, 0.0)
            diff = score_a - score_b
            
            # Clean name
            name = sub_key.split("_", 1)[1].replace("_", " ").title() if "_" in sub_key else sub_key
            
            diffs.append({
                "category": name,
                "diff": diff,
                "abs_diff": abs(diff),
                "group": criteria
            })
    
    # Sort by magnitude of difference (impact)
    diffs.sort(key=lambda x: x["diff"], reverse=True)
    return diffs

def plot_variance_chart(diffs):
    """
    Horizontal Bar Chart showing the 'Spread' or 'Alpha' between A and B.
    """
    # Sort for chart display (A winning at top, B winning at bottom)
    diffs_sorted = sorted(diffs, key=lambda x: x["diff"]) 
    
    categories = [d["category"] for d in diffs_sorted]
    values = [d["diff"] for d in diffs_sorted]
    colors = ['#00C805' if v > 0 else '#FF4B4B' for v in values]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=categories,
        x=values,
        orientation='h',
        marker_color=colors,
        text=[f"{v:+.2f}" for v in values],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Spread: %{x:+.4f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text="Relative Performance Spread (Alpha)",
            font=dict(size=14, color="#9CA3AF")
        ),
        xaxis=dict(
            title="Score Differential (A - B)",
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#464B5C',
            gridcolor='#262940',
            tickfont=dict(color='gray')
        ),
        yaxis=dict(
            tickfont=dict(color='white', size=10),
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500,
        margin=dict(l=150, r=20, t=40, b=40),
        showlegend=False
    )
    return fig

# --- PAGE RENDERERS ---

def render_dashboard(client, weights_config, default_weights):
    # ===== TOP HEADER BAR — AIS Controls =====
    st.markdown("""
    <div class="header-bar">
        <div>
            <div class="brand">📈 AIS Analyst Dashboard</div>
            <div class="brand-sub">Earnings Intelligence Platform</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Controls row at the top
    tickers_list, data_map = get_available_filters(client)

    if not tickers_list:
        st.warning("No data found in MongoDB.")
        st.stop()

    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([2, 1.5, 1.5, 5])

    with ctrl_col1:
        selected_ticker = st.selectbox("Company", tickers_list, label_visibility="collapsed",
                                       help="Select a company ticker", key="selected_ticker")

    with ctrl_col2:
        available_years = sorted(data_map[selected_ticker].keys(), reverse=True)
        selected_year = st.selectbox("Year", available_years, label_visibility="collapsed",
                                     help="Select fiscal year", key="selected_year")

    with ctrl_col3:
        available_quarters = data_map[selected_ticker][selected_year]
        selected_quarter = st.selectbox("Quarter", available_quarters, label_visibility="collapsed",
                                        help="Select quarter", key="selected_quarter")

    with ctrl_col4:
        st.empty()  # Spacer to push controls left

    st.divider()

    # ===== STRICT WEIGHT VALIDATION =====
    weight_errors = []

    # Check criteria weights sum
    crit_sum = sum(
        st.session_state.get(f"cw_{c}", 0)
        for c in default_weights["criteria_weights"]
    )
    if crit_sum != 100:
        weight_errors.append(f"**Criteria weights** sum to **{crit_sum}%** (must be 100%)")

    # Check each sub-criteria group
    for crit, subs in default_weights["sub_criteria_definitions"].items():
        sub_sum = sum(st.session_state.get(f"sw_{sk}", 0) for sk in subs)
        if sub_sum != 100:
            label = CRITERIA_DISPLAY.get(crit, crit.replace("_", " ").title())
            weight_errors.append(f"**{label}** sub-criteria sum to **{sub_sum}%** (must be 100%)")

    if weight_errors:
        st.error("⚖️ **Weights must sum to exactly 100% before analysis can run.**")
        for err in weight_errors:
            st.warning(err)
        st.info("👈 Adjust the sliders in the **Weight Configuration** panel or click **🔄 Reset**.")
        return # Stop rendering this page

    # 3. Fetch Data for Selection
    raw_sub_scores = calc_ais.fetch_quarter_data(client, selected_ticker, selected_year, selected_quarter)
    
    # Get Text AND Raw Score
    assessment_text, qualitative_data, raw_ais_score = get_qualitative_data(client, selected_ticker, selected_year, selected_quarter)

    if not raw_sub_scores:
        st.error("Data missing for this quarter.")
        return

    # 4. Perform Calculations (Live)
    clean_scores = calc_ais.normalize_db_scores(raw_sub_scores, weights_config)
    weighted_score = calc_ais.calculate_weighted_ais(weights_config, clean_scores)

    # Calculate Criteria-Level Scores manually for display
    criteria_breakdown = {}
    for criteria, criteria_weight in weights_config['criteria_weights'].items():
        sub_def = weights_config['sub_criteria_definitions'].get(criteria, {})
        db_sub_scores = clean_scores.get(criteria, {})
        c_sum = sum(db_sub_scores.get(k, 0.0) * w for k, w in sub_def.items())
        criteria_breakdown[criteria] = {
            "score": c_sum,
            "weight": criteria_weight,
            "contribution": c_sum * criteria_weight
        }

    # --- DASHBOARD LAYOUT ---

    # Header Section — Ticker + Scores
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title(f"{selected_ticker}")
        st.markdown(f"### Earnings Analysis | {selected_year} {selected_quarter}")
    
    with col2:
        # We split the right side into two small columns for the scores
        score_col_raw, score_col_weighted = st.columns(2)
        
        # Color Logic
        w_color = "#00C805" if weighted_score >= 0.8 else "#FF4B4B" if weighted_score < 0.5 else "#FFA500"
        
        with score_col_raw:
            st.markdown(f"""
                <div style="text-align: right; opacity: 0.7;">
                    <div class="sub-header">Simple AIS</div>
                    <h2 style="margin:0; color: #CCCCCC;">{raw_ais_score:.2f}</h2>
                </div>
            """, unsafe_allow_html=True)
            
        with score_col_weighted:
             st.markdown(f"""
                <div style="text-align: right;">
                    <div class="sub-header">Weighted AIS</div>
                    <h1 style="margin:0; color: {w_color}; font-size: 3rem;">{weighted_score:.4f}</h1>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # The "Why" (Assessment)
    st.markdown(f"""
    <div class="custom-card">
        <div class="sub-header">🤖 AI Assessment</div>
        <div class="highlight-text">{assessment_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # Main Criteria Breakdown
    st.subheader("🏗️ Weighted Criteria Contribution")
    c1, c2, c3, c4 = st.columns(4)
    
    mapping = {
        "earnings_quality": ("Earnings Quality", "💰", c1),
        "management_quality": ("Management", "👔", c2),
        "growth_potential": ("Strategy / Growth", "🚀", c3),
        "strategy_execution": ("Strategy / Growth", "🚀", c3),
        "business_risks": ("Business Risks", "⚠️", c4)
    }

    for key, val in criteria_breakdown.items():
        if key in mapping:
            label, icon, col = mapping[key]
            with col:
                st.metric(
                    label=f"{icon} {label}", 
                    value=f"{val['score']:.2f}",
                    delta=f"Contribution: {val['contribution']:.3f}",
                    delta_color="off"
                )

    st.divider()

    # --- Sub-Criteria Labels (moved up for use in both sections) ---
    SUB_CRITERIA_LABELS = {
        "growth_potential": {
            "1.1_market_expansion": "1.1 Market & Geographic Expansion",
            "1.2_product_development": "1.2 Product & Service Development",
            "1.3_ma_partnerships": "1.3 M&A and Partnerships",
            "1.4_digital_transformation": "1.4 Digital Transformation",
            "1.5_diversification": "1.5 Operational Efficiency & Diversification"
        },
        "earnings_quality": {
            "2.1_revenue_sustainability": "2.1 Revenue Quality & Sustainability",
            "2.2_cost_efficiency": "2.2 Cost Management & Efficiency",
            "2.3_cash_flow": "2.3 Capital & Cash Flow Management",
            "2.4_margins": "2.4 Profitability & Margin Analysis",
            "2.5_external_factors": "2.5 External Factors & Accounting"
        },
        "management_quality": {
            "3.1_strategy_execution": "3.1 Strategic Planning & Execution",
            "3.2_capital_allocation": "3.2 Capital & Financial Management",
            "3.3_adaptability": "3.3 Adaptability & Responsiveness",
            "3.4_leadership": "3.4 Leadership & Organizational Effectiveness",
            "3.5_operational_efficiency": "3.5 Operational & Cost Efficiency"
        },
        "business_risks": {
            "4.1_market_economic": "4.1 Market & Economic Risks",
            "4.2_financial_credit": "4.2 Credit & Financial Risks",
            "4.3_operational_compliance": "4.3 Operational & Compliance Risks",
            "4.4_strategic": "4.4 Strategic & Business Risks",
            "4.5_tech_product": "4.5 Product & Technological Risks"
        }
    }

    criteria_options = {
        "growth_potential": "🚀 Growth Potential",
        "earnings_quality": "💰 Earnings Quality",
        "management_quality": "👔 Quality of Management",
        "business_risks": "⚠️ Business Risks"
    }

    # Radar Chart & Context
    col_radar, col_details = st.columns([1, 1])

    with col_radar:
        st.subheader("🎯 20-Point Sub-Criteria Analysis")
        st.caption("💡 Use the dropdowns to highlight points on the chart →")

        # Get selected sub-criteria from deep dive section
        selected_sub_for_chart = st.session_state.get('reasoning_sub', None)

        # Interactive Plotly Chart with highlighting
        fig = plot_radar_chart(clean_scores, weights_config, selected_sub_for_chart)

        # Display the chart
        st.plotly_chart(fig, use_container_width=True, key="radar_chart")

    with col_details:
        st.subheader("🔍 Sub-Criteria Deep Dive")
        st.caption("💡 Selection highlights on chart ←")

        # Fetch reasoning data from MongoDB
        reasoning_data = calc_ais.fetch_quarter_reasoning(
            client, selected_ticker, selected_year, selected_quarter
        )

        # Two-level dropdown selection
        sel_criterion = st.selectbox(
            "Criterion",
            list(criteria_options.keys()),
            format_func=lambda x: criteria_options[x],
            key="reasoning_criterion"
        )

        sub_opts = SUB_CRITERIA_LABELS[sel_criterion]
        sel_sub = st.selectbox(
            "Sub-Criterion",
            list(sub_opts.keys()),
            format_func=lambda x: sub_opts[x],
            key="reasoning_sub"
        )

        # Get the score for selected sub-criterion
        score = clean_scores.get(sel_criterion, {}).get(sel_sub, 0.0)
        score_color = "#4CAF50" if score > 0 else "#F44336" if score < 0 else "#FFC107"

        # Build reasoning card
        if reasoning_data:
            reasoning = reasoning_data.get(sel_criterion, {}).get(sel_sub, {})
            if reasoning:
                rationale = reasoning.get("rationale", "No rationale available")
                evidence = reasoning.get("evidence", "No evidence available")
                strength = reasoning.get("evidence_strength", "Unknown")

                strength_colors = {
                    "Strong": "#4CAF50", "Moderate": "#2196F3",
                    "Weak": "#FF9800", "None": "#9E9E9E"
                }
                s_color = strength_colors.get(strength, "#9E9E9E")

                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1a1c2e 0%, #262940 100%);
                            border: 1px solid #3a3f55; border-radius: 12px; padding: 20px;
                            margin: 10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                        <span style="color: #E0E0E0; font-weight: 600; font-size: 1.05em;">
                            {sub_opts[sel_sub]}
                        </span>
                        <span style="background: {score_color}; color: white; padding: 4px 14px;
                                     border-radius: 20px; font-weight: 700; font-size: 1.1em;">
                            {score:+.1f}
                        </span>
                    </div>
                    <div style="border-top: 1px solid #3a3f55; padding-top: 12px;">
                        <div style="color: #9CA3AF; font-size: 0.8em; text-transform: uppercase;
                                    letter-spacing: 1px; margin-bottom: 6px;">Rationale</div>
                        <div style="color: #E5E7EB; margin-bottom: 14px; line-height: 1.5;">
                            {rationale}
                        </div>
                        <div style="color: #9CA3AF; font-size: 0.8em; text-transform: uppercase;
                                    letter-spacing: 1px; margin-bottom: 6px;">Key Evidence</div>
                        <div style="color: #B0BEC5; margin-bottom: 14px; font-style: italic;
                                    line-height: 1.5; border-left: 3px solid #3a3f55; padding-left: 12px;">
                            {evidence}
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="color: #9CA3AF; font-size: 0.8em;">Evidence Strength:</span>
                            <span style="background: {s_color}; color: white; padding: 3px 10px;
                                         border-radius: 10px; font-size: 0.8em; font-weight: 600;">
                                {strength}
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No reasoning available for this sub-criterion.")
        else:
            # Fallback: show score without reasoning
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1c2e 0%, #262940 100%);
                        border: 1px solid #3a3f55; border-radius: 12px; padding: 20px;
                        margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #E0E0E0; font-weight: 600;">{sub_opts[sel_sub]}</span>
                    <span style="background: {score_color}; color: white; padding: 4px 14px;
                                 border-radius: 20px; font-weight: 700; font-size: 1.1em;">
                        {score:+.1f}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption("💡 Reasoning data not yet available for this quarter. Run enrich_reasoning.py to generate.")

    st.markdown("---")

    # Raw Data Table (Hidden)
    with st.expander("Show Raw Data Calculation"):
        st.json(criteria_breakdown)
        st.write("Normalized Sub-Scores:")
        st.json(clean_scores)

def render_compare_page(client, weights_config, default_weights):
    st.markdown("""
    <div class="header-bar">
        <div>
            <div class="brand">⚔️ Compare Quarters</div>
            <div class="brand-sub">Head-to-Head Analysis</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tickers_list, data_map = get_available_filters(client)
    if not tickers_list:
        st.warning("No data found.")
        st.stop()

    # Input Columns
    col_a, col_mid, col_b = st.columns([1, 0.1, 1])

    with col_a:
        st.markdown("### Entity A")
        tick_a = st.selectbox("Company", tickers_list, key="c_tick_a")
        yrs_a = sorted(data_map[tick_a].keys(), reverse=True)
        yr_a = st.selectbox("Year", yrs_a, key="c_yr_a")
        qtrs_a = data_map[tick_a][yr_a]
        qtr_a = st.selectbox("Quarter", qtrs_a, key="c_qtr_a")

    with col_b:
        st.markdown("### Entity B")
        tick_b = st.selectbox("Company", tickers_list, key="c_tick_b")
        yrs_b = sorted(data_map[tick_b].keys(), reverse=True)
        yr_b = st.selectbox("Year", yrs_b, key="c_yr_b")
        qtrs_b = data_map[tick_b][yr_b]
        qtr_b = st.selectbox("Quarter", qtrs_b, key="c_qtr_b")

    st.divider()

    # Fetch Data
    raw_sub_a = calc_ais.fetch_quarter_data(client, tick_a, yr_a, qtr_a)
    raw_sub_b = calc_ais.fetch_quarter_data(client, tick_b, yr_b, qtr_b)
    
    if not raw_sub_a or not raw_sub_b:
        st.error("Data missing for one or both selections.")
        return

    # Calculate
    clean_a = calc_ais.normalize_db_scores(raw_sub_a, weights_config)
    score_a = calc_ais.calculate_weighted_ais(weights_config, clean_a)

    clean_b = calc_ais.normalize_db_scores(raw_sub_b, weights_config)
    score_b = calc_ais.calculate_weighted_ais(weights_config, clean_b)

    # --- CUSTOM VISUALS FOR COMPARISON ---
    st.markdown("""
    <style>
        .comparison-container {
            display: flex;
            justify-content: center;
            align-items: stretch;
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: linear-gradient(145deg, #1e2035 0%, #161824 100%);
            border: 1px solid #2e3148;
            border-radius: 12px;
            padding: 20px;
            flex: 1;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
            position: relative;
        }
        .metric-card.winner {
            border: 1px solid #00C805;
            box-shadow: 0 0 20px rgba(0, 200, 5, 0.2);
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }
        .metric-label {
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #9CA3AF;
            margin-bottom: 8px;
        }
        .metric-value {
            font-size: 2.5em;
            font-weight: 700;
            margin: 0;
            background: linear-gradient(90deg, #fff, #bbb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .metric-delta {
            font-size: 1.1em;
            font-weight: 600;
            margin-top: 8px;
            padding: 4px 12px;
            border-radius: 20px;
            display: inline-block;
        }
        .delta-pos { background-color: rgba(0, 200, 5, 0.15); color: #00C805; }
        .delta-neg { background-color: rgba(255, 75, 75, 0.15); color: #FF4B4B; }
        
        .vs-badge {
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-style: italic;
            font-size: 1.5em;
            color: #464B5C;
        }
    </style>
    """, unsafe_allow_html=True)

    # Calculate Logic for Visuals
    net_diff = score_b - score_a
    winner_a = "winner" if score_a > score_b else ""
    winner_b = "winner" if score_b > score_a else ""
    
    # Delta display
    if score_a >= score_b:
        d_a_cls = "delta-pos"
        d_a_txt = "👑 LEADER"
        d_b_cls = "delta-neg"
        d_b_txt = f"{net_diff:.4f}"
    else:
        d_a_cls = "delta-neg"
        d_a_txt = f"{-net_diff:.4f}"
        d_b_cls = "delta-pos"
        d_b_txt = "👑 LEADER"

    # HTML Render
    col_layout = st.columns([1, 0.2, 1])
    
    html_a = f"""
    <div class="metric-card {winner_a}">
        <div class="metric-label">{tick_a} {yr_a} {qtr_a}</div>
        <div class="metric-value">{score_a:.4f}</div>
        <div class="metric-delta {d_a_cls}">{d_a_txt}</div>
    </div>
    """
    
    html_b = f"""
    <div class="metric-card {winner_b}">
        <div class="metric-label">{tick_b} {yr_b} {qtr_b}</div>
        <div class="metric-value">{score_b:.4f}</div>
        <div class="metric-delta {d_b_cls}">{d_b_txt}</div>
    </div>
    """

    with col_layout[0]:
        st.markdown(html_a, unsafe_allow_html=True)
    
    with col_layout[1]:
        st.markdown('<div class="vs-badge" style="height: 100%;">VS</div>', unsafe_allow_html=True)

    with col_layout[2]:
        st.markdown(html_b, unsafe_allow_html=True)

    # Chart
    st.subheader("🎯 Comparative Analysis")
    fig = plot_comparison_radar_chart(
        clean_a, f"{tick_a} {qtr_a}",
        clean_b, f"{tick_b} {qtr_b}",
        weights_config
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- INSTITUTIONAL GRADE ANALYSIS ---
    diffs = calculate_score_differentials(clean_a, clean_b)
    
    st.markdown("---")
    st.subheader("🏦 Comparative Alpha Analysis")
    
    # 1. Executive Verdict
    net_diff = score_a - score_b
    
    # Smart Labeling
    if tick_a == tick_b:
        winner = f"{tick_a} {qtr_a} {yr_a}" if net_diff > 0 else f"{tick_b} {qtr_b} {yr_b}"
        label_a_context = f"{tick_a} {qtr_a} {yr_a}"
    else:
        winner = tick_a if net_diff > 0 else tick_b
        label_a_context = tick_a
        
    margin = abs(net_diff)
    
    # Identify top drivers
    top_driver = diffs[0] if net_diff > 0 else diffs[-1]
    driver_name = top_driver['category']
    
    verdict_color = "#00C805" if net_diff > 0 else "#FF4B4B"  # Green if A wins, Red if B wins (from A's perspective)
    
    st.markdown(f"""
    <div class="custom-card" style="border-left-color: {verdict_color};">
        <div class="sub-header">EXECUTIVE VERDICT</div>
        <div class="highlight-text">
            {winner} currently implies a stronger investment profile with a <b>{margin:.4f}</b> net score advantage. 
            The divergence is primarily driven by outperformance in <b>{driver_name}</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Key Drivers (Wins vs Risks)
    col_wins, col_losses = st.columns(2)
    
    with col_wins:
        st.markdown(f"#### ✅ {label_a_context} Advantages")
        # Get top 3 positive diffs
        wins = [d for d in diffs if d['diff'] > 0][:3]
        if wins:
            for w in wins:
                st.markdown(f"**+{w['diff']:.2f}** {w['category']}")
                st.progress(min(w['diff']/0.5, 1.0)) # Normalize for visual
        else:
            st.caption("No material advantages identified.")
            
    with col_losses:
        st.markdown(f"#### ⚠️ {label_a_context} Relative Weaknesses")
        # Get top 3 negative diffs (reverse sorted)
        losses = sorted([d for d in diffs if d['diff'] < 0], key=lambda x: x['diff'])[:3]
        if losses:
            for l in losses:
                st.markdown(f"**{l['diff']:.2f}** {l['category']}")
                st.progress(min(abs(l['diff'])/0.5, 1.0))
        else:
            st.caption("No material weaknesses identified.")

    # 3. Variance Chart
    st.markdown("### Strategy Variance")
    var_fig = plot_variance_chart(diffs)
    st.plotly_chart(var_fig, use_container_width=True)

    # 4. Qualitative "Tale of the Tape"
    st.markdown("---")
    st.subheader("📝 Qualitative Insights")
    
    # Fetch Qualitative Data
    _, qual_a, _ = get_qualitative_data(client, tick_a, yr_a, qtr_a)
    _, qual_b, _ = get_qualitative_data(client, tick_b, yr_b, qtr_b)
    
    label_b_context = f"{tick_b} {qtr_b} {yr_b}" if tick_a == tick_b else tick_b

    q_col1, q_col2 = st.columns(2)
    
    with q_col1:
        st.markdown(f"#### 🏛️ {label_a_context}")
        if qual_a:
            with st.expander("📊 Forward Guidance", expanded=True):
                guidance = qual_a.get('management_guidance', {})
                if guidance:
                    for k, v in guidance.items():
                        clean_k = k.replace("_", " ").title()
                        st.markdown(f"**{clean_k}:** {v}")
                else:
                    st.caption("No specific guidance provided.")

            with st.expander("⭐ Quarter Highlights", expanded=True):
                events = qual_a.get('key_events', [])
                if events:
                    for e in events:
                        st.markdown(f"- {e}")
                else:
                    st.caption("No key events logged.")
        else:
            st.warning("No qualitative data available.")

    with q_col2:
        st.markdown(f"#### 🏛️ {label_b_context}")
        if qual_b:
            with st.expander("📊 Forward Guidance", expanded=True):
                guidance = qual_b.get('management_guidance', {})
                if guidance:
                    for k, v in guidance.items():
                        clean_k = k.replace("_", " ").title()
                        st.markdown(f"**{clean_k}:** {v}")
                else:
                    st.caption("No specific guidance provided.")

            with st.expander("⭐ Quarter Highlights", expanded=True):
                events = qual_b.get('key_events', [])
                if events:
                    for e in events:
                        st.markdown(f"- {e}")
                else:
                    st.caption("No key events logged.")
        else:
            st.warning("No qualitative data available.")

def generate_quarter_sequence(anchor_year, anchor_quarter, num_quarters, data_map, ticker):
    """
    Generate a chronological list of (year, quarter) tuples going backwards
    from the anchor point. Only includes quarters that exist in data_map.
    """
    all_quarters = []
    for yr in sorted(data_map.get(ticker, {}).keys()):
        for q in sorted(data_map[ticker][yr]):
            all_quarters.append((yr, q))

    # Find the anchor index
    anchor = (str(anchor_year), anchor_quarter)
    if anchor not in all_quarters:
        return []

    anchor_idx = all_quarters.index(anchor)

    # Grab up to num_quarters ending at anchor (inclusive)
    start_idx = max(0, anchor_idx - num_quarters + 1)
    return all_quarters[start_idx:anchor_idx + 1]


def render_trend_page(client, weights_config, default_weights):
    st.markdown("""
    <div class="header-bar">
        <div>
            <div class="brand">INSTITUTIONAL TREND ANALYSIS</div>
            <div class="brand-sub">Weighted AIS Momentum, Regime & Decomposition</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tickers_list, data_map = get_available_filters(client)
    if not tickers_list:
        st.warning("No data found.")
        st.stop()

    # ===== STRICT WEIGHT VALIDATION =====
    weight_errors = []
    crit_sum = sum(
        st.session_state.get(f"cw_{c}", 0)
        for c in default_weights["criteria_weights"]
    )
    if crit_sum != 100:
        weight_errors.append(f"**Criteria weights** sum to **{crit_sum}%** (must be 100%)")
    for crit, subs in default_weights["sub_criteria_definitions"].items():
        sub_sum = sum(st.session_state.get(f"sw_{sk}", 0) for sk in subs)
        if sub_sum != 100:
            label = CRITERIA_DISPLAY.get(crit, crit.replace("_", " ").title())
            weight_errors.append(f"**{label}** sub-criteria sum to **{sub_sum}%** (must be 100%)")
    if weight_errors:
        st.error("Weights must sum to exactly 100% before analysis can run.")
        for err in weight_errors:
            st.warning(err)
        st.info("Adjust the sliders in the **Weight Configuration** panel or click **Reset**.")
        return

    # --- Controls ---
    ctrl1, ctrl2, ctrl3 = st.columns([2, 1.5, 1.5])
    with ctrl1:
        trend_ticker = st.selectbox(
            "Company", tickers_list, key="trend_ticker",
            label_visibility="collapsed", help="Select a company"
        )
    with ctrl2:
        trend_years = sorted(data_map[trend_ticker].keys(), reverse=True)
        trend_year = st.selectbox(
            "Year", trend_years, key="trend_year",
            label_visibility="collapsed", help="Anchor year"
        )
    with ctrl3:
        trend_qtrs = data_map[trend_ticker][trend_year]
        trend_qtr = st.selectbox(
            "Quarter", trend_qtrs, key="trend_qtr",
            label_visibility="collapsed", help="Anchor quarter (current)"
        )

    st.divider()

    # --- Slider + Toggle ---
    opt1, opt2 = st.columns([2, 1])
    with opt1:
        num_quarters = st.slider(
            "Number of Quarters", min_value=4, max_value=12, value=4, step=1,
            key="trend_num_q",
            help="Min 4 (same year) / Max 12 (spans ~3 years)"
        )
    with opt2:
        include_current = st.toggle(
            "Include Current Quarter", value=True, key="trend_include",
            help="ON = compare current quarter against historical moving average"
        )

    st.divider()

    # --- Build Quarter Sequence ---
    sequence = generate_quarter_sequence(
        trend_year, trend_qtr, num_quarters, data_map, trend_ticker
    )
    if len(sequence) < 2:
        st.warning("Not enough historical data for the selected range.")
        return

    # =================================================================
    #  DATA ENGINE — Fetch overall + criteria-level scores per quarter
    # =================================================================
    CRITERIA_KEYS = list(weights_config["criteria_weights"].keys())
    CRITERIA_SHORT = {
        "growth_potential": "Growth",
        "earnings_quality": "Earnings Qlty",
        "management_quality": "Mgmt Qlty",
        "business_risks": "Biz Risks",
    }

    quarter_labels = []
    scores = []
    criteria_series = {c: [] for c in CRITERIA_KEYS}  # per-criteria scores

    for yr, q in sequence:
        raw_sub = calc_ais.fetch_quarter_data(client, trend_ticker, yr, q)
        label = f"{q} {yr}"
        quarter_labels.append(label)
        if raw_sub:
            clean = calc_ais.normalize_db_scores(raw_sub, weights_config)
            w_score = calc_ais.calculate_weighted_ais(weights_config, clean)
            scores.append(w_score)
            # Criteria-level weighted contributions
            for crit in CRITERIA_KEYS:
                cw = weights_config["criteria_weights"][crit]
                sub_def = weights_config["sub_criteria_definitions"].get(crit, {})
                crit_subs = clean.get(crit, {})
                c_score = sum(crit_subs.get(k, 0.0) * w for k, w in sub_def.items())
                criteria_series[crit].append(c_score * cw)
        else:
            scores.append(None)
            for crit in CRITERIA_KEYS:
                criteria_series[crit].append(None)

    valid_scores = [s for s in scores if s is not None]
    if len(valid_scores) < 2:
        st.warning("Not enough valid data points.")
        return

    # =================================================================
    #  ANALYTICS ENGINE
    # =================================================================
    current_label = quarter_labels[-1]
    current_score = scores[-1]

    if include_current and current_score is not None:
        historical_scores = [s for s in scores[:-1] if s is not None]
    else:
        historical_scores = valid_scores

    if not historical_scores:
        st.warning("No valid historical scores to compute a moving average.")
        return

    # --- Dual Moving Averages (Short & Long) ---
    short_window = max(2, min(3, len(valid_scores) - 1))
    long_window = max(3, min(6, len(valid_scores)))

    def rolling_ma(data, window):
        """Compute rolling MA over a list, handling Nones."""
        result = []
        buf = []
        for v in data:
            if v is not None:
                buf.append(v)
            if len(buf) >= window:
                result.append(np.mean(buf[-window:]))
            elif buf:
                result.append(np.mean(buf))
            else:
                result.append(None)
        return result

    short_ma = rolling_ma(scores, short_window)
    long_ma = rolling_ma(scores, long_window)

    # --- Bollinger Bands (2-sigma around long MA) ---
    def rolling_std(data, window):
        result = []
        buf = []
        for v in data:
            if v is not None:
                buf.append(v)
            if len(buf) >= window:
                result.append(np.std(buf[-window:], ddof=1))
            elif len(buf) > 1:
                result.append(np.std(buf, ddof=1))
            else:
                result.append(0.0)
        return result

    long_std_series = rolling_std(scores, long_window)
    bb_upper = [m + 2 * s if m is not None else None for m, s in zip(long_ma, long_std_series)]
    bb_lower = [m - 2 * s if m is not None else None for m, s in zip(long_ma, long_std_series)]

    # --- Overall Statistics ---
    moving_avg = np.mean(historical_scores)
    moving_std = np.std(historical_scores, ddof=1) if len(historical_scores) > 1 else 0.0

    # --- QoQ Momentum ---
    qoq_changes = []
    for i in range(len(scores)):
        if i == 0 or scores[i] is None or scores[i - 1] is None:
            qoq_changes.append(0.0)
        else:
            qoq_changes.append(scores[i] - scores[i - 1])

    # --- Jump Detection ---
    jump = None
    jump_pct = None
    is_significant = False
    z_score_val = 0.0
    significance_threshold = 1.5

    if include_current and current_score is not None and historical_scores:
        jump = current_score - moving_avg
        jump_pct = (jump / moving_avg * 100) if moving_avg != 0 else 0.0
        if moving_std > 0:
            z_score_val = abs(jump) / moving_std
            is_significant = z_score_val >= significance_threshold
        else:
            is_significant = abs(jump) > 0.001

    # --- Risk Metrics ---
    # Peak-to-trough drawdown (uses historical only when current is separated)
    drawdown_scores = historical_scores if (include_current and current_score is not None) else valid_scores
    peak = drawdown_scores[0]
    max_drawdown = 0.0
    for s in drawdown_scores:
        if s > peak:
            peak = s
        dd = (peak - s) / peak if peak > 0 else 0.0
        if dd > max_drawdown:
            max_drawdown = dd

    # Consistency (% of quarters with positive QoQ change)
    pos_qoq = sum(1 for c in qoq_changes[1:] if c > 0)
    total_qoq = max(len(qoq_changes) - 1, 1)
    consistency = pos_qoq / total_qoq

    # Information Ratio (mean QoQ change / std of QoQ change — Sharpe analog)
    qoq_valid = [c for i, c in enumerate(qoq_changes)
                 if i > 0 and scores[i] is not None and scores[i - 1] is not None]
    if len(qoq_valid) > 1 and np.std(qoq_valid, ddof=1) > 0:
        info_ratio = np.mean(qoq_valid) / np.std(qoq_valid, ddof=1)
    else:
        info_ratio = 0.0

    # Trend slope via linear regression on valid scores
    xs = [i for i, s in enumerate(scores) if s is not None]
    ys = [s for s in scores if s is not None]
    if len(xs) >= 2:
        coeffs = np.polyfit(xs, ys, 1)
        trend_slope = coeffs[0]
    else:
        trend_slope = 0.0

    # --- Regime Detection ---
    if trend_slope > 0.005 and consistency >= 0.6:
        regime = "BULLISH"
        regime_color = "#00C805"
    elif trend_slope < -0.005 and consistency <= 0.4:
        regime = "BEARISH"
        regime_color = "#FF4B4B"
    else:
        regime = "CONSOLIDATION"
        regime_color = "#FFA500"

    # --- MA Crossover Signal ---
    crossover_signal = "NEUTRAL"
    if len(short_ma) >= 2 and len(long_ma) >= 2:
        s_curr, s_prev = short_ma[-1], short_ma[-2]
        l_curr, l_prev = long_ma[-1], long_ma[-2]
        if s_curr is not None and l_curr is not None and s_prev is not None and l_prev is not None:
            if s_prev <= l_prev and s_curr > l_curr:
                crossover_signal = "GOLDEN CROSS"
            elif s_prev >= l_prev and s_curr < l_curr:
                crossover_signal = "DEATH CROSS"

    # =================================================================
    #  SECTION 1 — EXECUTIVE VERDICT
    # =================================================================
    if include_current and jump is not None:
        if is_significant and jump > 0:
            verdict = "ACCELERATING — Fundamental Improvement Detected"
            v_color = "#00C805"
        elif is_significant and jump < 0:
            verdict = "DECELERATING — Fundamental Deterioration Detected"
            v_color = "#FF4B4B"
        else:
            verdict = "STEADY STATE — No Material Deviation from Trend"
            v_color = "#FFA500"
    else:
        verdict = f"REGIME: {regime}"
        v_color = regime_color

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
                border: 1px solid {v_color}; border-radius: 12px; padding: 20px 28px;
                margin-bottom: 24px; box-shadow: 0 0 30px {v_color}33;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="color: #6B7280; font-size: 0.75em; text-transform: uppercase;
                            letter-spacing: 2px; margin-bottom: 4px;">
                    {trend_ticker} | CONVICTION CALL</div>
                <div style="color: {v_color}; font-size: 1.6em; font-weight: 800;
                            letter-spacing: 0.5px;">{verdict}</div>
            </div>
            <div style="text-align: right;">
                <div style="color: #6B7280; font-size: 0.7em; text-transform: uppercase;
                            letter-spacing: 1.5px;">Regime</div>
                <div style="color: {regime_color}; font-size: 1.3em; font-weight: 700;">{regime}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =================================================================
    #  SECTION 2 — TOP METRICS ROW
    # =================================================================
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        st.metric("Weighted AIS", f"{current_score:.4f}" if current_score is not None else "N/A",
                   delta=f"Delta: {jump:+.4f}" if jump is not None else None,
                   help="The composite AIS score for the selected quarter, weighted by your criteria & sub-criteria sliders. Delta shows the deviation from the historical moving average (Current − MA).")
    with m2:
        st.metric(f"MA({long_window}Q)", f"{moving_avg:.4f}",
                   help=f"Simple Moving Average of the Weighted AIS over the last {long_window} quarters. Calculated as the arithmetic mean of historical scores, smoothing out quarter-to-quarter noise.")
    with m3:
        st.metric("Volatility (σ)", f"{moving_std:.4f}",
                   help="Standard deviation of historical Weighted AIS scores. Measures how much the score fluctuates quarter-to-quarter. Higher values indicate less predictable fundamentals.")
    with m4:
        st.metric("Max Drawdown", f"{max_drawdown:.1%}",
                   help="Largest peak-to-trough decline in Weighted AIS across the selected period. Calculated as (Peak − Trough) / Peak. Indicates the worst-case fundamental deterioration observed.")
    with m5:
        st.metric("Consistency", f"{consistency:.0%}",
                   help="Percentage of quarters that showed a positive QoQ (quarter-over-quarter) change in Weighted AIS. Higher values suggest steady fundamental improvement; lower values suggest erratic performance.")
    with m6:
        st.metric("Info Ratio", f"{info_ratio:.2f}",
                   help="Information Ratio — a Sharpe-like measure for fundamentals. Calculated as Mean(QoQ changes) / Std(QoQ changes). Positive values mean consistent improvement; negative values mean consistent decline.")

    st.divider()

    # =================================================================
    #  SECTION 3 — SIGNAL STRIP
    # =================================================================
    sig1, sig2, sig3, sig4 = st.columns(4)
    with sig1:
        jump_help = (
            "Detects whether the current quarter's score is a statistically significant departure from the historical trend. "
            f"Calculated as: z-score = |Current − MA| / σ. A z-score ≥ {significance_threshold} is flagged as SIGNIFICANT. "
            "Delta shows the % deviation from MA and the z-score value."
        )
        if include_current and jump is not None:
            direction = "UP" if jump > 0 else "DOWN"
            sig_label = f"SIGNIFICANT {direction}" if is_significant else "Normal"
            st.metric("Jump Signal", sig_label,
                       delta=f"{jump_pct:+.1f}% | z={z_score_val:.2f}" if jump is not None else None,
                       help=jump_help)
        else:
            st.metric("Jump Signal", "N/A", help=jump_help)
    with sig2:
        st.metric("MA Crossover", crossover_signal,
                   delta=f"Short MA({short_window}Q) vs Long MA({long_window}Q)",
                   delta_color="off",
                   help=f"Compares the Short MA ({short_window}Q) against the Long MA ({long_window}Q). "
                        "GOLDEN CROSS: Short MA crosses above Long MA — signals improving momentum. "
                        "DEATH CROSS: Short MA crosses below Long MA — signals deteriorating momentum. "
                        "NEUTRAL: No crossover detected in the latest period.")
    with sig3:
        slope_dir = "+" if trend_slope > 0 else ""
        st.metric("Trend Slope", f"{slope_dir}{trend_slope:.4f}/Q",
                   delta="Linear Regression",
                   delta_color="off",
                   help="The slope of an Ordinary Least Squares (OLS) linear regression fitted to the Weighted AIS scores over the selected quarters. "
                        "Represents the average change in AIS per quarter. "
                        "Positive = upward fundamental trend; Negative = downward fundamental trend.")
    with sig4:
        # Bollinger Band position
        if current_score is not None and bb_upper[-1] is not None and bb_lower[-1] is not None:
            bb_range = bb_upper[-1] - bb_lower[-1]
            if bb_range > 0:
                bb_pct = (current_score - bb_lower[-1]) / bb_range * 100
            else:
                bb_pct = 50.0
            bb_label = f"{bb_pct:.0f}%"
            if bb_pct > 90:
                bb_note = "Overbought"
            elif bb_pct < 10:
                bb_note = "Oversold"
            else:
                bb_note = "Mid-Band"
        else:
            bb_label = "N/A"
            bb_note = ""
        st.metric("Bollinger %B", bb_label,
                   delta=bb_note if bb_note else None,
                   delta_color="off",
                   help="Bollinger %B measures where the current score sits within the Bollinger Bands. "
                        "Calculated as: (Current − Lower Band) / (Upper Band − Lower Band) × 100. "
                        "Bands are set at ±2 standard deviations around the Long MA. "
                        "Above 90% = Overbought (score unusually high vs history). "
                        "Below 10% = Oversold (score unusually low vs history). "
                        "50% = exactly at the moving average.")

    st.divider()

    # =================================================================
    #  SECTION 4 — PRIMARY CHART (AIS + Dual MA + Bollinger Bands)
    # =================================================================
    st.subheader("AIS Score with Dual Moving Averages & Bollinger Bands")

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06,
        row_heights=[0.7, 0.3],
        subplot_titles=["", "QoQ Momentum"]
    )

    # --- Row 1: Bollinger Band fill ---
    fig.add_trace(go.Scatter(
        x=quarter_labels, y=bb_upper, mode='lines',
        line=dict(width=0), showlegend=False, hoverinfo='skip'
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=quarter_labels, y=bb_lower, mode='lines',
        line=dict(width=0), fill='tonexty',
        fillcolor='rgba(99,102,241,0.08)',
        name='Bollinger Band (2σ)', hoverinfo='skip'
    ), row=1, col=1)

    # --- Row 1: Long MA ---
    fig.add_trace(go.Scatter(
        x=quarter_labels, y=long_ma, mode='lines',
        name=f'Long MA ({long_window}Q)',
        line=dict(color='#FFA500', width=2, dash='dash'),
        hovertemplate='Long MA: %{y:.4f}<extra></extra>'
    ), row=1, col=1)

    # --- Row 1: Short MA ---
    fig.add_trace(go.Scatter(
        x=quarter_labels, y=short_ma, mode='lines',
        name=f'Short MA ({short_window}Q)',
        line=dict(color='#00BFFF', width=2),
        hovertemplate='Short MA: %{y:.4f}<extra></extra>'
    ), row=1, col=1)

    # --- Row 1: AIS Score line ---
    main_y = list(scores)
    if include_current and current_score is not None:
        main_y[-1] = None  # Gap — current plotted separately

    fig.add_trace(go.Scatter(
        x=quarter_labels, y=main_y,
        mode='lines+markers', name='Weighted AIS',
        line=dict(color='#6366F1', width=2.5),
        marker=dict(size=7, color='#6366F1', line=dict(width=2, color='white')),
        hovertemplate='<b>%{x}</b><br>AIS: %{y:.4f}<extra></extra>'
    ), row=1, col=1)

    # --- Row 1: Current quarter diamond ---
    if include_current and current_score is not None:
        m_color = '#00C805' if (jump and jump > 0) else '#FF4B4B' if (jump and jump < 0) else '#FFFFFF'
        fig.add_trace(go.Scatter(
            x=[current_label], y=[current_score],
            mode='markers+text', name=f'Current ({current_label})',
            marker=dict(size=14, color=m_color, symbol='diamond',
                        line=dict(width=3, color='white')),
            text=[f"{current_score:.4f}"], textposition='top center',
            textfont=dict(color='white', size=11, family='monospace'),
            hovertemplate='<b>%{x}</b><br>Current: %{y:.4f}<extra></extra>'
        ), row=1, col=1)
        # Connector
        if len(scores) >= 2 and scores[-2] is not None:
            fig.add_trace(go.Scatter(
                x=[quarter_labels[-2], current_label],
                y=[scores[-2], current_score],
                mode='lines', line=dict(color=m_color, width=2, dash='dot'),
                showlegend=False, hoverinfo='skip'
            ), row=1, col=1)

    # --- Row 1: Trend regression line ---
    if len(xs) >= 2:
        reg_y = [coeffs[0] * i + coeffs[1] for i in range(len(scores))]
        fig.add_trace(go.Scatter(
            x=quarter_labels, y=reg_y, mode='lines',
            name='Trend (OLS)', line=dict(color='#9CA3AF', width=1, dash='dashdot'),
            hoverinfo='skip'
        ), row=1, col=1)

    # --- Row 2: QoQ Momentum Bars ---
    bar_colors = ['#00C805' if c > 0 else '#FF4B4B' if c < 0 else '#464B5C' for c in qoq_changes]
    fig.add_trace(go.Bar(
        x=quarter_labels, y=qoq_changes, name='QoQ Change',
        marker_color=bar_colors,
        hovertemplate='<b>%{x}</b><br>QoQ: %{y:+.4f}<extra></extra>'
    ), row=2, col=1)

    # --- Layout ---
    fig.update_layout(
        height=560,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.04,
                    xanchor="right", x=1, font=dict(color="white", size=10)),
        margin=dict(l=60, r=20, t=30, b=40),
        hovermode="x unified",
        bargap=0.3
    )
    for row in [1, 2]:
        fig.update_xaxes(gridcolor='#1e2035', tickfont=dict(color='#9CA3AF'), row=row, col=1)
        fig.update_yaxes(gridcolor='#1e2035', tickfont=dict(color='#9CA3AF'), row=row, col=1)
    fig.update_xaxes(tickangle=-45, row=2, col=1)
    fig.update_yaxes(title_text="Weighted AIS", row=1, col=1)
    fig.update_yaxes(title_text="QoQ Δ", row=2, col=1, zeroline=True,
                     zerolinecolor='#464B5C', zerolinewidth=1)

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # =================================================================
    #  SECTION 5 — CRITERIA DECOMPOSITION
    # =================================================================
    st.subheader("Criteria Contribution Decomposition (Stacked)")

    fig_stack = go.Figure()
    crit_colors = {
        "growth_potential": "#6366F1",
        "earnings_quality": "#00C805",
        "management_quality": "#00BFFF",
        "business_risks": "#FF4B4B",
    }
    for crit in CRITERIA_KEYS:
        fig_stack.add_trace(go.Bar(
            x=quarter_labels,
            y=criteria_series[crit],
            name=CRITERIA_SHORT.get(crit, crit),
            marker_color=crit_colors.get(crit, "#9CA3AF"),
            hovertemplate=f'<b>%{{x}}</b><br>{CRITERIA_SHORT.get(crit, crit)}: %{{y:.4f}}<extra></extra>'
        ))

    fig_stack.update_layout(
        barmode='stack',
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, font=dict(color="white", size=10)),
        margin=dict(l=60, r=20, t=20, b=40),
        xaxis=dict(gridcolor='#1e2035', tickfont=dict(color='#9CA3AF'), tickangle=-45),
        yaxis=dict(title="Weighted Contribution", gridcolor='#1e2035',
                   tickfont=dict(color='#9CA3AF')),
        hovermode="x unified"
    )
    st.plotly_chart(fig_stack, use_container_width=True)

    # =================================================================
    #  SECTION 6 — INSTITUTIONAL DATA TABLE
    # =================================================================
    with st.expander("Full Quarter-by-Quarter Data", expanded=False):
        table_data = []
        for i, (lbl, s) in enumerate(zip(quarter_labels, scores)):
            row = {
                "Quarter": lbl,
                "Weighted AIS": f"{s:.4f}" if s is not None else "N/A",
            }
            # Per-criteria contributions
            for crit in CRITERIA_KEYS:
                cv = criteria_series[crit][i]
                row[CRITERIA_SHORT.get(crit, crit)] = f"{cv:.4f}" if cv is not None else "-"
            # QoQ
            if i > 0 and scores[i - 1] is not None and s is not None:
                d = s - scores[i - 1]
                row["QoQ Δ"] = f"{d:+.4f}"
                row["QoQ %"] = f"{(d / scores[i - 1] * 100):+.1f}%"
            else:
                row["QoQ Δ"] = "-"
                row["QoQ %"] = "-"
            # Short/Long MA
            row[f"MA({short_window}Q)"] = f"{short_ma[i]:.4f}" if short_ma[i] is not None else "-"
            row[f"MA({long_window}Q)"] = f"{long_ma[i]:.4f}" if long_ma[i] is not None else "-"
            # Bollinger position
            if s is not None and bb_upper[i] is not None and bb_lower[i] is not None:
                brange = bb_upper[i] - bb_lower[i]
                row["BB %B"] = f"{((s - bb_lower[i]) / brange * 100):.0f}%" if brange > 0 else "-"
            else:
                row["BB %B"] = "-"
            # Signal column for current
            if include_current and i == len(scores) - 1 and s is not None and jump is not None:
                row["Signal"] = "SIGNIFICANT" if is_significant else "Normal"
            else:
                row["Signal"] = "-"
            table_data.append(row)
        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)


# --- COMPANY BREAKDOWN PAGE ---

def render_company_breakdown(client, weights_config, default_weights):
    st.markdown("""
    <div class="header-bar">
        <div>
            <div class="brand">COMPANY BREAKDOWN</div>
            <div class="brand-sub">Institutional Historical Analysis & Sub-Criteria Trends</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tickers_list, data_map = get_available_filters(client)
    if not tickers_list:
        st.warning("No data found.")
        st.stop()

    # ===== WEIGHT VALIDATION =====
    weight_errors = []
    crit_sum = sum(
        st.session_state.get(f"cw_{c}", 0)
        for c in default_weights["criteria_weights"]
    )
    if crit_sum != 100:
        weight_errors.append(f"**Criteria weights** sum to **{crit_sum}%** (must be 100%)")
    for crit, subs in default_weights["sub_criteria_definitions"].items():
        sub_sum = sum(st.session_state.get(f"sw_{sk}", 0) for sk in subs)
        if sub_sum != 100:
            label = CRITERIA_DISPLAY.get(crit, crit.replace("_", " ").title())
            weight_errors.append(f"**{label}** sub-criteria sum to **{sub_sum}%** (must be 100%)")
    if weight_errors:
        st.error("Weights must sum to exactly 100% before analysis can run.")
        for err in weight_errors:
            st.warning(err)
        st.info("Adjust the sliders in the **Weight Configuration** panel or click **Reset**.")
        return

    # ===== COMPANY SELECTOR =====
    selected_ticker = st.selectbox(
        "Select Company",
        tickers_list,
        key="breakdown_ticker",
        help="Choose a company to view its full historical breakdown"
    )

    st.divider()

    # ===== BUILD FULL HISTORICAL DATA =====
    all_quarters = []
    for yr in sorted(data_map.get(selected_ticker, {}).keys()):
        for q in sorted(data_map[selected_ticker][yr]):
            all_quarters.append((yr, q))

    if not all_quarters:
        st.warning("No quarterly data available for this company.")
        return

    CRITERIA_KEYS = list(weights_config["criteria_weights"].keys())
    CRITERIA_SHORT = {
        "growth_potential": "Growth",
        "earnings_quality": "Earn Qlty",
        "management_quality": "Mgmt Qlty",
        "business_risks": "Biz Risks",
    }
    SUB_KEYS_ORDERED = []
    for crit in CRITERIA_KEYS:
        for sub_key in weights_config["sub_criteria_definitions"].get(crit, {}):
            SUB_KEYS_ORDERED.append((crit, sub_key))

    # --- Fetch all data ---
    raw_scores_per_quarter = []  # list of (label, yr, q, w_score, clean_scores, criteria_scores)
    trend_data = {sub_key: [] for _, sub_key in SUB_KEYS_ORDERED}
    trend_labels = []
    weighted_ais_series = []
    criteria_scores_series = {crit: [] for crit in CRITERIA_KEYS}

    for yr, q in all_quarters:
        raw_sub = calc_ais.fetch_quarter_data(client, selected_ticker, yr, q)
        label = f"{q} {yr}"
        trend_labels.append(label)

        if not raw_sub:
            for _, sub_key in SUB_KEYS_ORDERED:
                trend_data[sub_key].append(None)
            for crit in CRITERIA_KEYS:
                criteria_scores_series[crit].append(None)
            weighted_ais_series.append(None)
            raw_scores_per_quarter.append((label, yr, q, None, None, None))
            continue

        clean = calc_ais.normalize_db_scores(raw_sub, weights_config)
        w_score = calc_ais.calculate_weighted_ais(weights_config, clean)
        weighted_ais_series.append(w_score)

        crit_scores = {}
        for crit in CRITERIA_KEYS:
            sub_def = weights_config["sub_criteria_definitions"].get(crit, {})
            crit_subs = clean.get(crit, {})
            c_score = sum(crit_subs.get(k, 0.0) * w for k, w in sub_def.items())
            crit_scores[crit] = c_score
            criteria_scores_series[crit].append(c_score)

        for crit_key, sub_key in SUB_KEYS_ORDERED:
            score = clean.get(crit_key, {}).get(sub_key, 0.0)
            trend_data[sub_key].append(score)

        raw_scores_per_quarter.append((label, yr, q, w_score, clean, crit_scores))

    valid_scores = [s for s in weighted_ais_series if s is not None]
    if not valid_scores:
        st.warning("No valid score data for this company.")
        return

    # =================================================================
    #  SECTION 1: EXECUTIVE SUMMARY STRIP
    # =================================================================
    latest_score = valid_scores[-1]
    hist_avg = np.mean(valid_scores)
    hist_std = np.std(valid_scores, ddof=1) if len(valid_scores) > 1 else 0.0
    best_score = max(valid_scores)
    worst_score = min(valid_scores)

    # Find best/worst quarter labels
    best_idx = weighted_ais_series.index(best_score)
    worst_idx = weighted_ais_series.index(worst_score)
    best_label = trend_labels[best_idx]
    worst_label = trend_labels[worst_idx]

    # Streak: consecutive positive/negative QoQ changes from the latest quarter
    streak = 0
    streak_dir = ""
    for i in range(len(weighted_ais_series) - 1, 0, -1):
        curr = weighted_ais_series[i]
        prev = weighted_ais_series[i - 1]
        if curr is None or prev is None:
            break
        diff = curr - prev
        if streak == 0:
            streak_dir = "improvement" if diff > 0 else "decline" if diff < 0 else ""
            if diff == 0:
                break
            streak = 1
        else:
            if (streak_dir == "improvement" and diff > 0) or (streak_dir == "decline" and diff < 0):
                streak += 1
            else:
                break

    # Percentile of latest score in history
    percentile = sum(1 for s in valid_scores if s <= latest_score) / len(valid_scores) * 100

    # Trend slope (linear regression)
    xs = [i for i, s in enumerate(weighted_ais_series) if s is not None]
    ys = [s for s in weighted_ais_series if s is not None]
    trend_slope = np.polyfit(xs, ys, 1)[0] if len(xs) >= 2 else 0.0
    trend_direction = "Uptrend" if trend_slope > 0.003 else "Downtrend" if trend_slope < -0.003 else "Flat"

    # Executive summary cards
    st.subheader(f"Executive Summary — {selected_ticker}")

    ex1, ex2, ex3, ex4, ex5, ex6 = st.columns(6)
    with ex1:
        qoq_delta = None
        if len(valid_scores) >= 2:
            qoq_delta = valid_scores[-1] - valid_scores[-2]
        st.metric(
            "Latest AIS", f"{latest_score:.4f}",
            delta=f"QoQ: {qoq_delta:+.4f}" if qoq_delta is not None else None,
            help="Most recent quarter's Weighted AIS score with QoQ change"
        )
    with ex2:
        st.metric(
            "Historical Avg", f"{hist_avg:.4f}",
            delta=f"Std: {hist_std:.4f}",
            delta_color="off",
            help=f"Mean and standard deviation across {len(valid_scores)} quarters"
        )
    with ex3:
        st.metric(
            "Best Quarter", f"{best_score:.4f}",
            delta=best_label,
            delta_color="off",
            help="Highest Weighted AIS score achieved and the quarter it occurred"
        )
    with ex4:
        st.metric(
            "Worst Quarter", f"{worst_score:.4f}",
            delta=worst_label,
            delta_color="off",
            help="Lowest Weighted AIS score and the quarter it occurred"
        )
    with ex5:
        streak_text = f"{streak}Q {streak_dir}" if streak > 0 else "No streak"
        st.metric(
            "Current Streak", streak_text,
            delta=f"Trend: {trend_direction}",
            delta_color="off",
            help="Consecutive quarters of improvement or decline from latest quarter, plus OLS trend direction"
        )
    with ex6:
        st.metric(
            "Hist. Percentile", f"{percentile:.0f}th",
            delta=f"of {len(valid_scores)} quarters",
            delta_color="off",
            help="Where the latest score ranks in the full history (100th = best ever, 0th = worst ever)"
        )

    st.divider()

    # =================================================================
    #  SECTION 2: INSTITUTIONAL SCORE TABLE
    # =================================================================
    st.subheader(f"Full Quarterly Breakdown — {selected_ticker}")
    st.caption(f"{len(all_quarters)} quarters | {all_quarters[0][0]} {all_quarters[0][1]} to {all_quarters[-1][0]} {all_quarters[-1][1]}")

    # Build a lookup for YoY: (quarter_name, year) -> index
    quarter_lookup = {}
    for i, (yr, q) in enumerate(all_quarters):
        quarter_lookup[(q, yr)] = i

    table_rows = []
    for i, (label, yr, q, w_score, clean, crit_scores) in enumerate(raw_scores_per_quarter):
        if w_score is None:
            continue

        row = {"Quarter": label, "Weighted AIS": round(w_score, 4)}

        # --- QoQ Change ---
        prev_score = weighted_ais_series[i - 1] if i > 0 else None
        if prev_score is not None:
            qoq_abs = w_score - prev_score
            qoq_pct = (qoq_abs / abs(prev_score) * 100) if prev_score != 0 else 0.0
            row["QoQ Chg"] = round(qoq_abs, 4)
            row["QoQ %"] = f"{qoq_pct:+.1f}%"
        else:
            row["QoQ Chg"] = None
            row["QoQ %"] = "-"

        # --- YoY Change (same quarter, prior year) ---
        try:
            prior_year = str(int(yr) - 1)
            yoy_key = (q, prior_year)
            if yoy_key in quarter_lookup:
                yoy_idx = quarter_lookup[yoy_key]
                yoy_score = weighted_ais_series[yoy_idx]
                if yoy_score is not None:
                    yoy_abs = w_score - yoy_score
                    yoy_pct = (yoy_abs / abs(yoy_score) * 100) if yoy_score != 0 else 0.0
                    row["YoY Chg"] = round(yoy_abs, 4)
                    row["YoY %"] = f"{yoy_pct:+.1f}%"
                else:
                    row["YoY Chg"] = None
                    row["YoY %"] = "-"
            else:
                row["YoY Chg"] = None
                row["YoY %"] = "-"
        except (ValueError, KeyError):
            row["YoY Chg"] = None
            row["YoY %"] = "-"

        # --- Historical Percentile ---
        scores_up_to_now = [s for s in weighted_ais_series[:i + 1] if s is not None]
        if len(scores_up_to_now) >= 2:
            pctl = sum(1 for s in scores_up_to_now if s <= w_score) / len(scores_up_to_now) * 100
            row["Pctl"] = f"{pctl:.0f}th"
        else:
            row["Pctl"] = "-"

        # --- Criteria-level scores ---
        for crit in CRITERIA_KEYS:
            short = CRITERIA_SHORT.get(crit, crit)
            row[short] = round(crit_scores[crit], 4)

        # --- All 20 sub-criteria ---
        for crit_key, sub_key in SUB_KEYS_ORDERED:
            score = clean.get(crit_key, {}).get(sub_key, 0.0)
            display_name = SUB_CRITERIA_DISPLAY.get(sub_key, sub_key)
            row[display_name] = round(score, 2)

        table_rows.append(row)

    if table_rows:
        df = pd.DataFrame(table_rows)

        # --- Gradient heatmap for sub-criteria ---
        def heatmap_sub(val):
            """Gradient from red (-1) through neutral (0) to green (+1)."""
            if not isinstance(val, (int, float)):
                return ''
            clamped = max(-1.0, min(1.0, val))
            if clamped > 0:
                # Green gradient: more intense as score approaches +1
                intensity = int(clamped * 80)
                return f'background-color: rgba(0, 200, 5, {intensity / 100}); color: white'
            elif clamped < 0:
                # Red gradient: more intense as score approaches -1
                intensity = int(abs(clamped) * 80)
                return f'background-color: rgba(255, 75, 75, {intensity / 100}); color: white'
            else:
                return 'background-color: rgba(255, 193, 7, 0.2); color: #FFC107'

        def style_qoq(val):
            """Color QoQ change values."""
            if not isinstance(val, (int, float)):
                return ''
            if val > 0:
                return 'color: #00C805; font-weight: 600'
            elif val < 0:
                return 'color: #FF4B4B; font-weight: 600'
            return 'color: #9CA3AF'

        def style_ais(val):
            if not isinstance(val, (int, float)):
                return ''
            if val >= 0.8:
                return 'color: #00C805; font-weight: 700'
            elif val < 0.5:
                return 'color: #FF4B4B; font-weight: 700'
            return 'color: #FFA500; font-weight: 700'

        styled = df.style.map(style_ais, subset=["Weighted AIS"])

        # QoQ and YoY change columns
        for col_name in ["QoQ Chg", "YoY Chg"]:
            if col_name in df.columns:
                styled = styled.map(style_qoq, subset=[col_name])

        # Heatmap on all 20 sub-criteria columns
        sub_cols = [SUB_CRITERIA_DISPLAY.get(sk, sk) for _, sk in SUB_KEYS_ORDERED]
        existing_sub_cols = [c for c in sub_cols if c in df.columns]
        if existing_sub_cols:
            styled = styled.map(heatmap_sub, subset=existing_sub_cols)

        # Criteria-level columns colored
        crit_col_names = [CRITERIA_SHORT.get(c, c) for c in CRITERIA_KEYS]
        existing_crit_cols = [c for c in crit_col_names if c in df.columns]
        if existing_crit_cols:
            styled = styled.map(style_qoq, subset=existing_crit_cols)

        st.dataframe(styled, use_container_width=True, hide_index=True, height=500)

        # Download
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Full Breakdown as CSV",
            data=csv,
            file_name=f"{selected_ticker}_institutional_breakdown.csv",
            mime="text/csv",
            key="breakdown_csv"
        )
    else:
        st.warning("No score data available for this company.")

    st.divider()

    # =================================================================
    #  SECTION 3: INTERACTIVE SUB-CRITERIA TREND CHART
    # =================================================================
    st.subheader(f"Sub-Criteria Trend Analysis — {selected_ticker}")
    st.caption("Select sub-criteria below to plot their raw scores over time. Colors grouped by criteria.")

    CRITERIA_COLORS = {
        "growth_potential": ["#6366F1", "#818CF8", "#A5B4FC", "#C7D2FE", "#E0E7FF"],
        "earnings_quality": ["#10B981", "#34D399", "#6EE7B7", "#A7F3D0", "#D1FAE5"],
        "management_quality": ["#06B6D4", "#22D3EE", "#67E8F9", "#A5F3FC", "#CFFAFE"],
        "business_risks": ["#EF4444", "#F87171", "#FCA5A5", "#FECACA", "#FEE2E2"],
    }

    selected_subs = []

    checkbox_cols = st.columns(4)
    for idx, crit in enumerate(CRITERIA_KEYS):
        with checkbox_cols[idx]:
            crit_display = CRITERIA_DISPLAY.get(crit, crit)
            st.markdown(f"**{crit_display}**")

            sub_defs = weights_config["sub_criteria_definitions"].get(crit, {})
            for sub_key in sub_defs:
                sub_display = SUB_CRITERIA_DISPLAY.get(sub_key, sub_key)
                if st.checkbox(sub_display, key=f"bd_cb_{sub_key}"):
                    selected_subs.append((crit, sub_key))

    if not selected_subs:
        st.info("Select one or more sub-criteria above to see their trend lines.")
    else:
        # --- Main Trend Chart with QoQ momentum subplot ---
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
            row_heights=[0.7, 0.3],
            subplot_titles=["", "QoQ Score Change"]
        )

        for crit, sub_key in selected_subs:
            sub_display = SUB_CRITERIA_DISPLAY.get(sub_key, sub_key)
            crit_color_palette = CRITERIA_COLORS.get(crit, ["#9CA3AF"] * 5)
            sub_keys_in_crit = list(weights_config["sub_criteria_definitions"].get(crit, {}).keys())
            color_idx = sub_keys_in_crit.index(sub_key) if sub_key in sub_keys_in_crit else 0
            line_color = crit_color_palette[color_idx % len(crit_color_palette)]

            y_values = trend_data[sub_key]

            # Row 1: Score line
            fig.add_trace(go.Scatter(
                x=trend_labels,
                y=y_values,
                mode='lines+markers',
                name=sub_display,
                line=dict(color=line_color, width=2.5),
                marker=dict(size=5, line=dict(width=1, color='white')),
                hovertemplate=f'<b>{sub_display}</b><br>%{{x}}<br>Score: %{{y:.2f}}<extra></extra>',
                connectgaps=True,
                legendgroup=sub_key,
            ), row=1, col=1)

            # Row 2: QoQ change bars
            qoq_vals = [0.0]
            for j in range(1, len(y_values)):
                if y_values[j] is not None and y_values[j - 1] is not None:
                    qoq_vals.append(y_values[j] - y_values[j - 1])
                else:
                    qoq_vals.append(0.0)

            bar_colors = [line_color if v >= 0 else '#FF4B4B' for v in qoq_vals]
            fig.add_trace(go.Bar(
                x=trend_labels,
                y=qoq_vals,
                name=f"{sub_display} QoQ",
                marker_color=bar_colors,
                opacity=0.6,
                hovertemplate=f'<b>{sub_display}</b><br>%{{x}}<br>QoQ: %{{y:+.2f}}<extra></extra>',
                showlegend=False,
                legendgroup=sub_key,
            ), row=2, col=1)

        # Zero lines
        fig.add_hline(y=0, line_dash="dash", line_color="#464B5C", line_width=1, row=1, col=1)
        fig.add_hline(y=0, line_dash="dash", line_color="#464B5C", line_width=1, row=2, col=1)

        fig.update_layout(
            height=600,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=11),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.04,
                xanchor="left", x=0,
                font=dict(color="white", size=10)
            ),
            margin=dict(l=60, r=20, t=40, b=60),
            hovermode="x unified",
            barmode="group",
            bargap=0.3,
        )
        for row in [1, 2]:
            fig.update_xaxes(gridcolor='#1e2035', tickfont=dict(color='#9CA3AF'), row=row, col=1)
            fig.update_yaxes(gridcolor='#1e2035', tickfont=dict(color='#9CA3AF'), row=row, col=1)
        fig.update_xaxes(tickangle=-45, row=2, col=1)
        fig.update_yaxes(title_text="Raw Score", range=[-1.15, 1.15], zeroline=True,
                         zerolinecolor='#464B5C', row=1, col=1)
        fig.update_yaxes(title_text="QoQ Delta", zeroline=True,
                         zerolinecolor='#464B5C', row=2, col=1)

        st.plotly_chart(fig, use_container_width=True)

        # --- Institutional Summary Stats Table for selected subs ---
        st.markdown("#### Selected Sub-Criteria — Statistical Profile")

        stat_rows = []
        for crit, sub_key in selected_subs:
            sub_display = SUB_CRITERIA_DISPLAY.get(sub_key, sub_key)
            vals = [v for v in trend_data[sub_key] if v is not None]
            if not vals:
                continue
            # QoQ changes for this sub
            sub_qoq = []
            all_vals = trend_data[sub_key]
            for j in range(1, len(all_vals)):
                if all_vals[j] is not None and all_vals[j - 1] is not None:
                    sub_qoq.append(all_vals[j] - all_vals[j - 1])
            pos_qoq = sum(1 for c in sub_qoq if c > 0) if sub_qoq else 0
            consistency = (pos_qoq / len(sub_qoq) * 100) if sub_qoq else 0.0

            stat_rows.append({
                "Sub-Criteria": sub_display,
                "Latest": f"{vals[-1]:+.2f}",
                "Avg": f"{np.mean(vals):+.2f}",
                "Std Dev": f"{np.std(vals, ddof=1):.2f}" if len(vals) > 1 else "-",
                "Min": f"{min(vals):+.2f}",
                "Max": f"{max(vals):+.2f}",
                "Range": f"{max(vals) - min(vals):.2f}",
                "Consistency": f"{consistency:.0f}%",
                "Quarters": len(vals),
            })

        if stat_rows:
            st.dataframe(pd.DataFrame(stat_rows), use_container_width=True, hide_index=True)


# --- MAIN APP LOGIC ---

def main():
    # 1. Initialize
    try:
        client = init_connection()
        default_weights = calc_ais.load_weights_config()
    except Exception as e:
        st.error(f"Connection Error: {e}")
        st.stop()

    # Seed session state with defaults on first load
    init_default_weights()

    # ===== LEFT SIDEBAR — Navigation + Weight Config =====
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        st.markdown("---")

        # Initialize page state
        if 'page' not in st.session_state:
            st.session_state['page'] = 'dashboard'

        def set_page(page_name):
            st.session_state['page'] = page_name

        # Navigation Buttons
        st.button("📊 Dashboard", key="nav_dashboard", 
                 on_click=set_page, args=('dashboard',), use_container_width=True)
        st.button("🔍 Compare Quarters", key="nav_compare",
                 on_click=set_page, args=('compare',), use_container_width=True)
        st.button("📈 Trend & Moving Avg", key="nav_trend",
                 on_click=set_page, args=('trend',), use_container_width=True)
        st.button("🏢 Company Breakdown", key="nav_breakdown",
                 on_click=set_page, args=('breakdown',), use_container_width=True)

        st.markdown("---")

        # ===== Weight Configuration Section =====
        with st.expander("⚖️ Weight Configuration", expanded=False):
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                st.button("🔄 Reset", key="reset_weights",
                          on_click=reset_weights_to_defaults, use_container_width=True)
            with btn_col2:
                st.button("💾 Save", key="save_weights",
                          on_click=save_weights_to_file, args=(default_weights,),
                          use_container_width=True)

            st.markdown('<div class="weight-section-header">Criteria Weights</div>',
                        unsafe_allow_html=True)

            for crit in default_weights["criteria_weights"]:
                display = CRITERIA_DISPLAY.get(crit, crit.replace("_", " ").title())
                st.slider(
                    display,
                    min_value=0, max_value=100, step=5,
                    key=f"cw_{crit}",
                    format="%d%%",
                )

            # Criteria sum validation
            crit_sum = sum(
                st.session_state.get(f"cw_{c}", 0)
                for c in default_weights["criteria_weights"]
            )
            if crit_sum == 100:
                st.markdown('<span class="weight-sum-ok">✓ Sum: 100%</span>',
                            unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<span class="weight-sum-warn">⚠ Sum: {crit_sum}% (should be 100%)</span>',
                    unsafe_allow_html=True,
                )

            st.markdown("---")
            st.markdown('<div class="weight-section-header">Sub-Criteria Weights</div>',
                        unsafe_allow_html=True)

            for crit, subs in default_weights["sub_criteria_definitions"].items():
                crit_label = CRITERIA_DISPLAY.get(crit, crit.replace("_", " ").title())
                with st.expander(crit_label, expanded=False):
                    for sub_key in subs:
                        sub_display = SUB_CRITERIA_DISPLAY.get(
                            sub_key, sub_key.split("_", 1)[1].replace("_", " ").title()
                        )
                        st.slider(
                            sub_display,
                            min_value=0, max_value=100, step=5,
                            key=f"sw_{sub_key}",
                            format="%d%%",
                        )

                    # Sub-criteria sum validation
                    sub_sum = sum(
                        st.session_state.get(f"sw_{sk}", 0) for sk in subs
                    )
                    if sub_sum == 100:
                        st.markdown('<span class="weight-sum-ok">✓ Sum: 100%</span>',
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(
                            f'<span class="weight-sum-warn">⚠ Sum: {sub_sum}% (should be 100%)</span>',
                            unsafe_allow_html=True,
                        )

        st.caption("v1.0 • AIS Analyst Suite")

    # Build the live weights_config from current slider values
    weights_config = build_weights_from_ui(default_weights)

    # --- ROUTING LOGIC ---
    if st.session_state['page'] == 'dashboard':
        render_dashboard(client, weights_config, default_weights)
    elif st.session_state['page'] == 'compare':
        render_compare_page(client, weights_config, default_weights)
    elif st.session_state['page'] == 'trend':
        render_trend_page(client, weights_config, default_weights)
    elif st.session_state['page'] == 'breakdown':
        render_company_breakdown(client, weights_config, default_weights)
    else:
        st.info("🚧 Page under construction")

if __name__ == "__main__":
    main()
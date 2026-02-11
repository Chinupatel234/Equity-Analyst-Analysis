import streamlit as st
import plotly.graph_objects as go
import pandas as pd
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
def plot_radar_chart(normalized_scores, weights_config):
    """Creates an Interactive Radar Chart"""
    categories = []
    values = []
    
    # Flatten the dictionary
    for criteria, subs in normalized_scores.items():
        for sub_key, score in subs.items():
            # Clean key name (remove "1.1_")
            clean_name = sub_key.split("_", 1)[1].replace("_", " ").title() if "_" in sub_key else sub_key
            categories.append(clean_name)
            values.append(score)
    
    # Close the loop for radar chart
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='AIS Score',
        line_color='#FF4B4B',
        fillcolor='rgba(255, 75, 75, 0.2)',
        mode='lines+markers',  # Added markers for easier hovering
        marker=dict(size=6),
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
        hovermode="closest" # Ensures the closest point highlights
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

    # Radar Chart & Context
    col_radar, col_details = st.columns([1, 1])

    with col_radar:
        st.subheader("🎯 20-Point Sub-Criteria Analysis")
        # Interactive Plotly Chart
        fig = plot_radar_chart(clean_scores, weights_config)
        st.plotly_chart(fig, use_container_width=True)

    with col_details:
        st.subheader("📝 Qualitative Context")
        
        if qualitative_data:
            with st.expander("📌 Key Events", expanded=True):
                events = qualitative_data.get('key_events', [])
                for e in events:
                    st.markdown(f"- {e}")
            
            with st.expander("🔮 Management Guidance", expanded=True):
                guidance = qualitative_data.get('management_guidance', {})
                for k, v in guidance.items():
                    clean_k = k.replace("_", " ").title()
                    st.markdown(f"**{clean_k}:** {v}")
        else:
            st.info("No qualitative highlights available for this quarter.")

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
            with st.expander("🔮 Management Guidance", expanded=True):
                guidance = qual_a.get('management_guidance', {})
                if guidance:
                    for k, v in guidance.items():
                        clean_k = k.replace("_", " ").title()
                        st.markdown(f"**{clean_k}:** {v}")
                else:
                    st.caption("No specific guidance provided.")
            
            with st.expander("📌 Key Events", expanded=True):
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
            with st.expander("🔮 Management Guidance", expanded=True):
                guidance = qual_b.get('management_guidance', {})
                if guidance:
                    for k, v in guidance.items():
                        clean_k = k.replace("_", " ").title()
                        st.markdown(f"**{clean_k}:** {v}")
                else:
                    st.caption("No specific guidance provided.")
            
            with st.expander("📌 Key Events", expanded=True):
                events = qual_b.get('key_events', [])
                if events:
                    for e in events:
                        st.markdown(f"- {e}")
                else:
                    st.caption("No key events logged.")
        else:
            st.warning("No qualitative data available.")

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
        st.button("🔔 Alerts & Watchlist", key="nav_alerts", use_container_width=True)
        st.button("📄 Reports", key="nav_reports", use_container_width=True)
        st.button("⚙️ Settings", key="nav_settings", use_container_width=True)

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
    else:
        st.info("🚧 Page under construction")

if __name__ == "__main__":
    main()
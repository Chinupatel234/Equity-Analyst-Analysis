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
</style>
""", unsafe_allow_html=True)

# --- DATA LOADING FUNCTIONS ---
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

# --- MAIN APP LOGIC ---

def main():
    # 1. Initialize
    try:
        client = init_connection()
        weights_config = calc_ais.load_weights_config()
    except Exception as e:
        st.error(f"Connection Error: {e}")
        st.stop()

    # 2. Sidebar Controls
    with st.sidebar:
        st.title("📊 AIS Controls")
        
        tickers_list, data_map = get_available_filters(client)
        
        if not tickers_list:
            st.warning("No data found in MongoDB.")
            st.stop()

        selected_ticker = st.selectbox("Select Company", tickers_list)
        
        available_years = sorted(data_map[selected_ticker].keys(), reverse=True)
        selected_year = st.selectbox("Select Year", available_years)
        
        available_quarters = data_map[selected_ticker][selected_year]
        selected_quarter = st.selectbox("Select Quarter", available_quarters)
        
        st.markdown("---")
        st.caption("Weight Configuration Loaded: `ais_weights.json`")

    # 3. Fetch Data for Selection
    # NOTE: We ensure calc_ais.fetch_quarter_data exists in your restored file
    raw_sub_scores = calc_ais.fetch_quarter_data(client, selected_ticker, selected_year, selected_quarter)
    
    # Get Text AND Raw Score
    assessment_text, qualitative_data, raw_ais_score = get_qualitative_data(client, selected_ticker, selected_year, selected_quarter)

    if not raw_sub_scores:
        st.error("Data missing for this quarter.")
        st.stop()

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

    # Header Section
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
                    <div class="sub-header">Raw AIS</div>
                    <h2 style="margin:0; color: #CCCCCC;">{raw_ais_score:.2f}</h2>
                </div>
            """, unsafe_allow_html=True)
            
        with score_col_weighted:
             st.markdown(f"""
                <div style="text-align: right;">
                    <div class="sub-header">Weighted</div>
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
                    delta=f"Impact: {val['contribution']:.3f}",
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

if __name__ == "__main__":
    main()
    
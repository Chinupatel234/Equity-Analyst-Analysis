# we will use the weights which are stored in ais_weights.json
import json
import os
import certifi # ensure pip install certifi
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

# --- CONFIGURATION ---
WEIGHTS_FILE = "ais_weights.json"
DB_NAME = "EarningsAnalytics"
COLLECTION_NAME = "companies"

# --- 1. SETUP & UTILS ---
def get_mongo_connection():
    """Load .env and connect to MongoDB."""
    current_dir = Path(__file__).resolve().parent
    env_path = current_dir / ".env"
    load_dotenv(dotenv_path=env_path)
    
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("⚠️  MONGO_URI not found. Ensure .env is set.")
        return None
    
    # Use certifi for SSL verification
    return MongoClient(mongo_uri, tlsCAFile=certifi.where())

def load_weights_config():
    """Load the JSON weights definition."""
    if not os.path.exists(WEIGHTS_FILE):
        raise FileNotFoundError(f"Could not find {WEIGHTS_FILE}")
    
    with open(WEIGHTS_FILE, 'r') as f:
        return json.load(f)

# --- 2. DATA FETCHING (MISSING FUNCTION RESTORED) ---
def fetch_quarter_data(client, ticker, year, quarter):
    """
    Queries MongoDB for a specific company > year > quarter.
    Retrieves the 'sub_criteria_scores' dictionary.
    """
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    doc = collection.find_one({"_id": ticker})
    
    if not doc:
        return None

    # Navigate the nested JSON structure
    try:
        quarter_data = doc.get("years", {}).get(str(year), {}).get(quarter, {})
        ais_analysis = quarter_data.get("ais_analysis", {})
        sub_scores = ais_analysis.get("sub_criteria_scores", {})
        
        return sub_scores
    except AttributeError:
        return None

def fetch_quarter_metadata(client, ticker, year, quarter):
    """
    Retrieves metadata like call_date for a specific company > year > quarter.
    """
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    doc = collection.find_one({"_id": ticker})
    
    if not doc:
        return None

    try:
        quarter_data = doc.get("years", {}).get(str(year), {}).get(quarter, {})
        if not quarter_data:
            return None
            
        return {
            "call_date": quarter_data.get("call_date"),
            "transcript_id": quarter_data.get("transcript_id")
        }
    except AttributeError:
        return None

# --- 2. DATA NORMALIZATION ---
def normalize_db_scores(db_scores, weights_config):
    """
    Ensures scores from DB match the structure expected by weights file.
    Maps keys (e.g., '1.1_market_expansion') to config keys.
    """
    normalized_input = {}
    
    for main_crit, sub_crit_dict in weights_config['sub_criteria_definitions'].items():
        normalized_input[main_crit] = {}
        
        # Get sub-dictionary from DB
        db_category_data = db_scores.get(main_crit, {})
        
        for sub_key in sub_crit_dict.keys():
            # Get score, default to 0.0 if missing
            score = db_category_data.get(sub_key, 0.0)
            normalized_input[main_crit][sub_key] = score
            
    return normalized_input

# --- 3. CALCULATION ENGINE ---
def calculate_weighted_ais(weights_config, input_scores, verbose=False):
    """
    Calculates the AIS Score based on weights configuration.
    Returns the total weighted score.
    """
    total_weighted_score = 0
    
    if verbose:
        print(f"\n{' CRITERIA / SUB-CRITERIA': <45} | {' SCORE ': <8} | {' WEIGHT ': <8} | {' W. AVG '}")
        print("=" * 90)

    # Loop through the 4 Main Criteria
    for criteria, criteria_weight in weights_config['criteria_weights'].items():
        sub_def = weights_config['sub_criteria_definitions'].get(criteria, {})
        db_sub_scores = input_scores.get(criteria, {})
        
        criteria_sum = 0
        
        if verbose:
            print(f"🔹 {criteria.upper().replace('_', ' ')} (Weight: {criteria_weight:.0%})")
            print("-" * 90)

        for sub_key, sub_weight in sub_def.items():
            raw_score = db_sub_scores.get(sub_key, 0.0)
            weighted_sub = raw_score * sub_weight
            criteria_sum += weighted_sub
            
            if verbose:
                display_key = sub_key.split('_', 1)[1] if '_' in sub_key else sub_key
                print(f"   • {display_key: <40} | {raw_score: <8.2f} | {sub_weight: <8.2f} | {weighted_sub: .3f}")

        criteria_contribution = criteria_sum * criteria_weight
        total_weighted_score += criteria_contribution

        if verbose:
            print("-" * 90)
            print(f"   👉 {criteria.upper()} SCORE: {criteria_sum:.4f}  (Contrib: {criteria_contribution:.4f})")
            print("=" * 90)

    return total_weighted_score

# --- 4. BATCH PROCESSING ---
def process_all_data(client, weights):
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    # Fetch all documents (companies)
    cursor = collection.find({})
    
    summary_results = []

    print(f"🚀 Starting Batch Processing (2018-2025)...\n")

    for doc in cursor:
        ticker = doc.get('_id')
        years_data = doc.get('years', {})
        
        # Sort years to ensure chronological processing
        sorted_years = sorted(years_data.keys())

        for year in sorted_years:
            # Filter for requested range 2018-2025
            if not year.isdigit(): continue
            year_int = int(year)
            if not (2018 <= year_int <= 2025):
                continue
            
            quarters_data = years_data[year]
            # Sort quarters (Q1, Q2, Q3, Q4)
            for quarter in sorted(quarters_data.keys()):
                
                # Navigate JSON path to get scores
                q_data = quarters_data[quarter]
                ais_analysis = q_data.get('ais_analysis', {})
                
                # Try to get the pre-calculated 'overall_score' from DB if it exists
                # (This is likely the unweighted or previously calculated score)
                raw_ais_score = ais_analysis.get('overall_score', 0.0)
                
                sub_scores = ais_analysis.get('sub_criteria_scores', {})

                if sub_scores:
                    # 1. Normalize Keys
                    clean_scores = normalize_db_scores(sub_scores, weights)
                    
                    # 2. Calculate Weighted Score
                    final_weighted_score = calculate_weighted_ais(weights, clean_scores, verbose=False)
                    
                    # 3. Store Result
                    summary_results.append({
                        "Ticker": ticker,
                        "Year": year,
                        "Quarter": quarter,
                        "AIS": raw_ais_score,          # Original DB Score
                        "Weighted_AIS": final_weighted_score # Newly Calculated Score
                    })
                    print(f"✅ Calculated {ticker} {year} {quarter}: {final_weighted_score:.4f}")
                else:
                    pass

    return summary_results

# --- MAIN EXECUTION ---
# --- MAIN EXECUTION (FOR TESTING ONLY) ---
# if __name__ == "__main__":
#     try:
#         weights = load_weights_config()
#         client = get_mongo_connection()
#         if client:
#             results = process_all_data(client, weights)
#             print(f"Processed {len(results)} records.")
#     except Exception as e:
#         print(f"Error: {e}")

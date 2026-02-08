import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv
from anthropic import Anthropic
import calc_ais

# --- SETUP ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL_NAME = "claude-opus-4-6" # latest anthropic model

# --- HELPER: TICKER NORMALIZATION ---
TICKER_ALIASES = {
    "google": "GOOG",
    "alphabet": "GOOG",
    "googl": "GOOG",
    "microsoft": "MSFT",
    "amazon": "AMZN",
    "meta": "META",
    "facebook": "META",
    "fb": "META"
}

def normalize_ticker(ticker: str) -> str:
    """Convert company names or aliases to standard ticker symbols."""
    ticker_clean = ticker.strip().upper()
    # Check if it's an alias
    alias_match = TICKER_ALIASES.get(ticker.lower())
    if alias_match:
        return alias_match
    return ticker_clean

# --- HELPER: DATA VALIDATION ---
def validate_ticker(ticker: str, mongo_client) -> bool:
    """Fast check if ticker exists in DB to prevent hallucinations/wasted logic."""
    db = mongo_client[calc_ais.DB_NAME]
    collection = db[calc_ais.COLLECTION_NAME]
    ticker_normalized = normalize_ticker(ticker)
    return collection.find_one({"_id": ticker_normalized}) is not None

# --- TOOLS IMPLEMENTATION ---
def tool_get_top_companies(year, quarter=None, top_n=5):
    mongo_client = None
    try:
        mongo_client = calc_ais.get_mongo_connection()
        weights = calc_ais.load_weights_config()
        
        # 1. Fetch All
        results = calc_ais.process_all_data(mongo_client, weights)
        
        # 2. Filter
        filtered = [r for r in results if str(r['Year']) == str(year)]
        if quarter:
            filtered = [r for r in filtered if r['Quarter'] == quarter]
            
        # 3. Sort & Slice
        filtered.sort(key=lambda x: x['Weighted_AIS'], reverse=True)
        top_picks = filtered[:top_n]
        
        if not top_picks:
            return json.dumps({"error": f"No data found for {year} {quarter if quarter else ''}"})

        return json.dumps(top_picks)
    finally:
        if mongo_client:
            mongo_client.close()

def tool_analyze_sub_criteria(ticker, year, quarter):
    mongo_client = None
    try:
        mongo_client = calc_ais.get_mongo_connection()
        ticker = normalize_ticker(ticker)  # Normalize first
        if not validate_ticker(ticker, mongo_client):
            return json.dumps({"error": f"Ticker '{ticker}' not found in database. Available tickers: MSFT, GOOG, AMZN, META"})

        weights = calc_ais.load_weights_config()
        data = calc_ais.fetch_quarter_data(mongo_client, ticker, year, quarter)
        
        if not data:
            return json.dumps({"error": "Data not found for this period"})
            
        clean_scores = calc_ais.normalize_db_scores(data, weights)
        
        # Calculate main criteria scores (weighted averages)
        main_criteria_scores = {}
        for crit, subs in clean_scores.items():
            if subs:  # Avoid division by zero
                main_criteria_scores[crit] = round(sum(subs.values()) / len(subs), 2)
        
        # Get qualitative context
        qualitative = data.get('qualitative_highlights', {})
        
        return json.dumps({
            "sub_criteria_scores": clean_scores,
            "main_criteria_scores": main_criteria_scores,
            "qualitative": qualitative
        })
    finally:
        if mongo_client:
            mongo_client.close()

def tool_get_score_trend(ticker, criteria_name, start_year, end_year):
    mongo_client = calc_ais.get_mongo_connection()
    ticker = normalize_ticker(ticker)  # Normalize first
    if not validate_ticker(ticker, mongo_client):
        return json.dumps({"error": f"Ticker '{ticker}' not found. Available: MSFT, GOOG, AMZN, META"})

    weights = calc_ais.load_weights_config()
    db = mongo_client[calc_ais.DB_NAME]
    collection = db[calc_ais.COLLECTION_NAME]
    
    doc = collection.find_one({"_id": ticker})
    
    # SMART MAPPING
    # Maps user language to DB keys
    SYNONYM_MAP = {
        "innovation": "1.2_product_development",
        "product": "1.2_product_development",
        "market": "1.1_market_expansion",
        "margins": "2.4_margins",
        "leadership": "3.4_leadership",
        "strategy": "3.1_strategy_execution",
        "risk": "business_risks",
        "earnings": "earnings_quality",
        "growth": "growth_potential"
    }
    
    target_key = criteria_name.lower()
    # Try direct map, otherwise fallback to loose matching
    mapped_key = SYNONYM_MAP.get(target_key, target_key)

    trend_data = []
    
    # Handle Year Range
    try:
        years = range(int(start_year), int(end_year) + 1)
    except (ValueError, TypeError) as e:
        return json.dumps({"error": f"Invalid year range: {str(e)}"})

    for year in years:
        year_str = str(year)
        if year_str in doc.get('years', {}):
            for q in sorted(doc['years'][year_str].keys()):
                try:
                    q_data = doc['years'][year_str][q]
                    sub_scores = q_data['ais_analysis'].get('sub_criteria_scores', {})
                    if not sub_scores: continue
                    
                    clean_scores = calc_ais.normalize_db_scores(sub_scores, weights)
                    found_val = None

                    # 1. Exact Key Match in Sub-Criteria (e.g. '1.1_market_expansion')
                    for cat, subs in clean_scores.items():
                        if mapped_key in subs:
                            found_val = subs[mapped_key]
                            break
                            
                    # 2. Main Criteria Aggregate (e.g. 'Growth Potential')
                    if found_val is None:
                        if mapped_key in clean_scores:
                             vals = clean_scores[mapped_key].values()
                             found_val = sum(vals) / len(vals)
                        elif criteria_name.replace(" ", "_").lower() in clean_scores:
                             # Try original name if mapping failed
                             key = criteria_name.replace(" ", "_").lower()
                             vals = clean_scores[key].values()
                             found_val = sum(vals) / len(vals)

                    # 3. Fuzzy Search (Last Resort)
                    if found_val is None:
                        for cat, subs in clean_scores.items():
                            for k, v in subs.items():
                                if mapped_key in k.lower():
                                    found_val = v
                                    break
                    
                    if found_val is not None:
                        trend_data.append({
                            "period": f"{year_str} {q}",
                            "score": round(found_val, 3)
                        })
                except Exception as e:
                    continue

    if not trend_data:
        return json.dumps({"result": f"No trend data found for '{criteria_name}' (mapped to '{mapped_key}'). Try a different metric name."})

    if mongo_client:
        mongo_client.close()
    return json.dumps({"ticker": ticker, "metric": criteria_name, "trend": trend_data})

def tool_compare_companies(ticker_a, ticker_b, year, quarter):
    mongo_client = None
    try:
        mongo_client = calc_ais.get_mongo_connection()
        ticker_a = normalize_ticker(ticker_a)  # Normalize both
        ticker_b = normalize_ticker(ticker_b)
        if not validate_ticker(ticker_a, mongo_client) or not validate_ticker(ticker_b, mongo_client):
            return json.dumps({"error": f"One or both tickers not found. Available: MSFT, GOOG, AMZN, META"})

        weights = calc_ais.load_weights_config()
        
        def get_company_scores(ticker):
            raw_data = calc_ais.fetch_quarter_data(mongo_client, ticker, year, quarter)
            if not raw_data: return None
            clean = calc_ais.normalize_db_scores(raw_data, weights)
            
            main_scores = {}
            for crit, crit_weight in weights['criteria_weights'].items():
                sub_def = weights['sub_criteria_definitions'].get(crit, {})
                sub_scores = clean.get(crit, {})
                cat_sum = sum(sub_scores.get(k, 0.0) * w for k, w in sub_def.items())
                main_scores[crit] = round(cat_sum, 3)
            return main_scores

        scores_a = get_company_scores(ticker_a)
        scores_b = get_company_scores(ticker_b)
        
        if not scores_a or not scores_b:
            return json.dumps({"error": f"Data missing for one or both companies in {year} {quarter}"})
            
        return json.dumps({
            "comparison_period": f"{year} {quarter}",
            "company_A": {"ticker": ticker_a, "scores": scores_a},
            "company_B": {"ticker": ticker_b, "scores": scores_b}
        })
    finally:
        if mongo_client:
            mongo_client.close()

def tool_search_qualitative(query, year):
    mongo_client = None
    try:
        mongo_client = calc_ais.get_mongo_connection()
        db = mongo_client[calc_ais.DB_NAME]
        collection = db[calc_ais.COLLECTION_NAME]
        
        results = []
        cursor = collection.find({})
        
        for doc in cursor:
            ticker = doc.get('_id')
            year_data = doc.get('years', {}).get(str(year), {})
            
            for q, data in year_data.items():
                if not isinstance(data, dict): continue
                
                texts_to_search = []
                texts_to_search.append(data.get('ais_analysis', {}).get('assessment', ''))
                qual = data.get('qualitative_highlights', {})
                texts_to_search.extend(qual.get('key_events', []))
                guidance = qual.get('management_guidance', {})
                texts_to_search.extend(guidance.values())
                
                matches = [t for t in texts_to_search if query.lower() in t.lower()]
                
                if matches:
                    results.append({
                        "ticker": ticker,
                        "quarter": q,
                        "snippets": matches[:2]
                    })
                    
        if not results:
            return json.dumps({"result": "No mentions found for that topic."})
            
    finally:
        if mongo_client:
            mongo_client.close()

# --- HELPER: STOCK PRICE FETCHING ---
def get_stock_price(ticker: str, start_date: str, end_date: str) -> List[Dict]:
    """
    Fetches daily OHLC data from Yahoo Finance Chart API.
    Dates should be in 'YYYY-MM-DD' format.
    """
    # Yahoo Finance API expects unix timestamp
    try:
        dt_start = datetime.strptime(start_date, "%Y-%m-%d")
        dt_end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) # Include end date
        
        period1 = int(dt_start.timestamp())
        period2 = int(dt_end.timestamp())
        
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={period1}&period2={period2}&interval=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if "chart" not in data or "result" not in data["chart"] or not data["chart"]["result"]:
            return []
            
        result = data["chart"]["result"][0]
        timestamps = result["timestamp"]
        indicators = result["indicators"]["quote"][0]
        opens = indicators["open"]
        closes = indicators["close"]
        
        prices = []
        for i, ts in enumerate(timestamps):
            if opens[i] is None or closes[i] is None: continue
            date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            prices.append({
                "date": date_str,
                "open": opens[i],
                "close": closes[i]
            })
            
        return prices
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return []

import re

def get_earnings_timing(ticker: str) -> tuple[str, str]:
    """
    Returns (timing, source).
    Timing: 'AMC' or 'BMO'
    Source: 'Static Map', 'Dynamic Scrape', or 'Fallback Assumption'
    """
    # 1. Static Map (Primary - Highest Reliability for Demo)
    timing_map = {
        "MSFT": "AMC",
        "GOOG": "AMC", "GOOGL": "AMC",
        "AMZN": "AMC",
        "META": "AMC", "FB": "AMC",
        "NVDA": "AMC",
        "TSLA": "AMC",
        "AAPL": "AMC",
        "NFLX": "AMC" 
    }
    
    ticker_upper = ticker.upper()
    if ticker_upper in timing_map:
        return timing_map[ticker_upper], "Static Map"

    # 2. Dynamic Scrape (Secondary)
    print(f"⚠️ Ticker {ticker} not in static map. Attempting dynamic lookup...")
    url = f"https://finance.yahoo.com/quote/{ticker}"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        text = response.text.lower()
        
        if "after market" in text or "market close" in text:
            return "AMC", "Dynamic Scrape (Yahoo)"
        
        if "before market" in text or "market open" in text:
            return "BMO", "Dynamic Scrape (Yahoo)"
            
    except Exception as e:
        print(f"Dynamic scrape failed: {e}")

    # 3. Fallback
    return "AMC", "Fallback Assumption"

def tool_get_earnings_price_impact(ticker, year, quarter):
    mongo_client = None
    try:
        mongo_client = calc_ais.get_mongo_connection()
        ticker = normalize_ticker(ticker)
        
        # 1. Get Earnings Date from DB
        metadata = calc_ais.fetch_quarter_metadata(mongo_client, ticker, year, quarter)
        if not metadata or not metadata.get("call_date"):
            return json.dumps({"error": f"Earnings date not found for {ticker} {year} {quarter}"})
            
        call_date_str = metadata["call_date"]
        call_date = datetime.strptime(call_date_str, "%Y-%m-%d")
        
        timing, timing_source = get_earnings_timing(ticker)
        
        # 2. Determine Before/After Dates based on Timing
        # Logic:
        # If AMC (After Market Close) on Jan 20: 
        #   Price Before = Close on Jan 20
        #   Price After = Open on Jan 21
        #   (Impact = Overnight change)
        
        # If BMO (Before Market Open) on Jan 20:
        #   Price Before = Close on Jan 19
        #   Price After = Open on Jan 20
        
        if timing == "AMC":
            date_before = call_date
            # Next trading day (simplified, API will skip weekends)
            date_after = call_date + timedelta(days=5) 
        else: # BMO
            date_before = call_date - timedelta(days=5)
            date_after = call_date
            
        # Fetch range to ensure we hit trading days
        fetch_start = (date_before - timedelta(days=5)).strftime("%Y-%m-%d")
        fetch_end = (date_after + timedelta(days=5)).strftime("%Y-%m-%d")
        
        prices = get_stock_price(ticker, fetch_start, fetch_end)
        if not prices:
             return json.dumps({"error": "Could not fetch stock prices from external API."})
             
        # Find exact price points
        price_before_node = None
        price_after_node = None
        
        if timing == "AMC":
            # Before = Close of call date (or nearest previous)
            # After = Open of next trading day
            for p in prices:
                if p["date"] <= call_date_str:
                    price_before_node = p # continually update to get latest before/on date
                if p["date"] > call_date_str and price_after_node is None:
                    price_after_node = p
                    break
                    
            if price_before_node: val_before = price_before_node["close"]
            if price_after_node: val_after = price_after_node["open"]
            
        else: # BMO
            # Before = Close of previous trading day
            # After = Open of call date (or nearest next)
            for p in prices:
                if p["date"] < call_date_str:
                    price_before_node = p
                if p["date"] >= call_date_str and price_after_node is None:
                    price_after_node = p
                    break
            
            if price_before_node: val_before = price_before_node["close"]
            if price_after_node: val_after = price_after_node["open"]

        if not price_before_node or not price_after_node:
             return json.dumps({"error": f"Could not find trading data around {call_date_str}."})
             
        pct_change = ((val_after - val_before) / val_before) * 100
        
        return json.dumps({
            "ticker": ticker,
            "period": f"{year} {quarter}",
            "earnings_date": call_date_str,
            "timing_assumption": f"{timing} ({timing_source})",
            "price_before_earnings": {
                "date": price_before_node["date"],
                "price": round(val_before, 2),
                "type": "Close"
            },
            "price_after_earnings": {
                "date": price_after_node["date"],
                "price": round(val_after, 2),
                "type": "Open"
            },
            "percent_change_impact": f"{pct_change:.2f}%"
        })

    finally:
        if mongo_client:
            mongo_client.close()

# --- TOOL SCHEMA DEFINITIONS ---
tools_schema = [
    {
        "name": "get_top_companies",
        "description": "Get a ranking of companies based on AIS scores. Use this for general performance queries.",
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {"type": "string"},
                "quarter": {"type": "string"},
                "top_n": {"type": "integer"}
            },
            "required": ["year"]
        }
    },
    {
        "name": "analyze_sub_criteria",
        "description": "Get detailed scores and qualitative explanations for a specific company.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "year": {"type": "string"},
                "quarter": {"type": "string"}
            },
            "required": ["ticker", "year", "quarter"]
        }
    },
    {
        "name": "get_score_trend",
        "description": "Get historical score data for a specific metric (e.g., 'Innovation', 'Margins', 'Management') over time.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "criteria_name": {"type": "string"},
                "start_year": {"type": "integer"},
                "end_year": {"type": "integer"}
            },
            "required": ["ticker", "criteria_name", "start_year", "end_year"]
        }
    },
    {
        "name": "compare_companies",
        "description": "Compare two companies side-by-side on main criteria scores.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker_a": {"type": "string"},
                "ticker_b": {"type": "string"},
                "year": {"type": "string"},
                "quarter": {"type": "string"}
            },
            "required": ["ticker_a", "ticker_b", "year", "quarter"]
        }
    },
    {
        "name": "search_qualitative",
        "description": "Search text across all companies for keywords like 'AI', 'Layoffs', 'Dividend'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "year": {"type": "string"}
            },
            "required": ["query", "year"]
        }
    },
    {
        "name": "get_earnings_price_impact",
        "description": "Calculate stock price change before and after earnings call. Returns price before, after, and % change.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "year": {"type": "string"},
                "quarter": {"type": "string"}
            },
            "required": ["ticker", "year", "quarter"]
        }
    }
]

# --- MAIN AGENT LOOP ---

def process_tool_call(tool_name, tool_input):
    """Router to dispatch the correct tool function."""
    try:
        if tool_name == "get_top_companies":
            return tool_get_top_companies(tool_input["year"], tool_input.get("quarter"), tool_input.get("top_n", 5))
        elif tool_name == "analyze_sub_criteria":
            return tool_analyze_sub_criteria(tool_input["ticker"], tool_input["year"], tool_input["quarter"])
        elif tool_name == "get_score_trend":
            return tool_get_score_trend(tool_input["ticker"], tool_input["criteria_name"], tool_input["start_year"], tool_input["end_year"])
        elif tool_name == "compare_companies":
            return tool_compare_companies(tool_input["ticker_a"], tool_input["ticker_b"], tool_input["year"], tool_input["quarter"])
        elif tool_name == "search_qualitative":
            return tool_search_qualitative(tool_input["query"], tool_input["year"])
        elif tool_name == "get_earnings_price_impact":
            return tool_get_earnings_price_impact(tool_input["ticker"], tool_input.get("year"), tool_input.get("quarter"))
    except Exception as e:
        return json.dumps({"error": f"Tool execution failed: {str(e)}"})

def ask_analyst_agent(user_query):
    """
    Main entry point. Handles the conversation loop including PARALLEL and MULTI-TURN tool calls.
    """
    print(f"\nUser: {user_query}")

    # Add system guidance as a user message
    system_guidance = """You are an AIS (Attractiveness Investment Score) analyst assistant.

Available companies in the database:
- Microsoft (MSFT)
- Google/Alphabet (GOOG)
- Amazon (AMZN)
- Meta/Facebook (META)

IMPORTANT: Always use these exact ticker symbols when calling tools. The tools will handle variations automatically.

When a user asks about a company not in this list (like Apple, Tesla, etc.), immediately inform them that the company is not available in the database rather than attempting multiple queries."""

    messages = [
        {"role": "user", "content": system_guidance},
        {"role": "assistant", "content": "Understood. I will only work with the available companies (MSFT, GOOG, AMZN, META) and use the correct ticker symbols."},
        {"role": "user", "content": user_query}
    ]

    # Helper function to safely extract text from response
    def extract_response_text(response):
        """Safely extract text from LLM response, handling various content types."""
        if not response.content:
            return "I apologize, but I couldn't generate a response."
        
        for block in response.content:
            if hasattr(block, 'text') and block.text:
                return block.text
        
        # Fallback: try to get any string representation
        return "I processed your request but couldn't format a text response."

    # Multi-turn loop with safety limit
    MAX_TOOL_TURNS = 5
    turn_count = 0

    try:
        while turn_count < MAX_TOOL_TURNS:
            turn_count += 1
            
            # Call LLM
            response = client.messages.create(
                model=MODEL_NAME,
                max_tokens=2000,
                tools=tools_schema,
                messages=messages
            )

            # Check if LLM wants to use tools
            if response.stop_reason == "tool_use":
                print(f"🤖 Agent decided to use tools (turn {turn_count})...")
                
                # Append the Assistant's "intent" to use tools to history
                messages.append({"role": "assistant", "content": response.content})
                
                # Prepare a list to hold ALL tool results (Anthropic requirement for parallel calls)
                tool_results_content = []

                # Loop through ALL tool requests in the response
                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_name = content_block.name
                        tool_input = content_block.input
                        tool_use_id = content_block.id
                        
                        print(f"   🔧 Executing: {tool_name} inputs={tool_input}")
                        
                        # Execute Python Function
                        result_data = process_tool_call(tool_name, tool_input)
                        
                        # Handle case where tool returns None
                        if result_data is None:
                            result_data = json.dumps({"error": "Tool returned no data"})
                        
                        # Add result to the batch
                        tool_results_content.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": result_data
                        })

                # Send ALL results back in a SINGLE user message
                messages.append({
                    "role": "user",
                    "content": tool_results_content
                })
                
                # Continue loop - LLM might request more tools
                continue
            
            else:
                # No more tools needed - extract and return final response
                final_text = extract_response_text(response)
                print(f"🤖 Agent: {final_text}")
                return final_text

        # Safety limit reached
        logging.warning(f"Max tool turns ({MAX_TOOL_TURNS}) reached for query: {user_query}")
        return "I've processed multiple steps but need to stop here. Please try a more specific query."

    except Exception as e:
        error_msg = f"An error occurred while processing your request: {str(e)}"
        logging.error(error_msg)
        print(f"❌ Error: {error_msg}")
        return error_msg

if __name__ == "__main__":
    # Test cases
    # ask_analyst_agent("Which companies mentioned 'AI' in 2024?")
    ask_analyst_agent("What was the stock price impact of Amazon's Q1 2025 earnings and Google's Q1 2025 earnings? Compare them and tell me which one performed better, along with the reason why.")

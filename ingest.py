# earnings_analysis_analyst_edition.json will be used to ingest the JSON into MongoDB
import json
import os
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("Error: MONGO_URI not found. Please check your .env file.")
    exit()

# 2. Configuration
DB_NAME = "EarningsAnalytics"
COLLECTION_NAME = "companies"
FILE_PATH = os.path.join("data", "earnings_analysis_analyst_edition.json")

def push_to_mongo():
    client = None
    try:
        # Connect to MongoDB
        print("Connecting to MongoDB...")
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Read the JSON file
        print(f"Reading file: {FILE_PATH}")
        with open(FILE_PATH, 'r') as file:
            raw_data = json.load(file)

        # 3. Transform Data
        # Your JSON has a "companies" key. We want each company (GOOG, MSFT, etc.)
        # to be its own document in the database for better querying.
        
        operations = []
        companies_data = raw_data.get("companies", {})
        
        if not companies_data:
            print("No 'companies' key found in JSON. Please check file structure.")
            return

        print(f"Found {len(companies_data)} companies. Preparing bulk write...")

        for ticker, company_info in companies_data.items():
            # We inject the ticker inside the object so it's part of the data
            company_info['ticker'] = ticker
            
            # We use the ticker as the unique ID (_id) to avoid duplicates if you run this script twice
            # This creates an 'upsert' operation (Update if exists, Insert if not)
            operation = UpdateOne(
                {"_id": ticker},           # Filter: Look for this ticker
                {"$set": company_info},    # Action: Update with new data
                upsert=True                # Option: Create if it doesn't exist
            )
            operations.append(operation)

        # 4. Execute Bulk Write (Much faster than inserting one by one)
        if operations:
            result = collection.bulk_write(operations)
            print("------------------------------------------------")
            print(f"Success! Database Updated.")
            print(f"Matched/Updated: {result.matched_count}")
            print(f"Newly Inserted:  {result.upserted_count}")
            print("------------------------------------------------")
        else:
            print("No operations generated.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if client is not None:
            client.close()

if __name__ == "__main__":
    push_to_mongo()

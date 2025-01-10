from datetime import datetime
import json
import requests
from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth

LRS_ENDPOINT = "https://lrsels.lip6.fr/data/xAPI"
LRS_USERNAME = "9fe9fa9a494f2b34b3cf355dcf20219d7be35b14"
LRS_PASSWORD = "b547a66817be9c2dbad2a5f583e704397c9db809"
XAPI_VERSION = "1.0.3"

headers = {
    "X-Experience-API-Version": XAPI_VERSION,
    "Content-Type": "application/json"
}

VERBS = [
    "http://adlnet.gov/expapi/verbs/completed",
    "http://adlnet.gov/expapi/verbs/launched",
    "https://spy.lip6.fr/xapi/verbs/executed"
]

def fetch_statements(user_id, verb):
    """
    Fetch all statements for a given user and verb.
    """
    query_params = {
        "agent": json.dumps({
            "account": {
                "homePage": "https://www.lip6.fr/mocah/",
                "name": user_id
            }
        }),
        "verb": verb
    }

    response = requests.get(
        f"{LRS_ENDPOINT}/statements",
        auth=HTTPBasicAuth(LRS_USERNAME, LRS_PASSWORD),
        params=query_params,
        headers=headers
    )

    if response.status_code != 200:
        print(f"Failed to query LRS for user {user_id} and verb {verb}: {response.status_code}")
        return []

    data_store = []
    response_json = response.json()
    process_lrs_response(response_json, data_store)
    return data_store

def process_lrs_response(response_json, data_store):
    """
    Process LRS response, handling pagination.
    """
    statements = response_json.get("statements", [])
    data_store.extend(statements)

    more_url = response_json.get("more")
    if more_url:
        full_more_url = urljoin(LRS_ENDPOINT, more_url)
        response = requests.get(
            full_more_url,
            auth=HTTPBasicAuth(LRS_USERNAME, LRS_PASSWORD),
            headers=headers
        )
        if response.status_code == 200:
            process_lrs_response(response.json(), data_store)
        else:
            print(f"Error fetching more data: {response.status_code} - {response.text}")

def download_statements(user_ids):
    """
    Download statements for multiple users and verbs, with deduplication.
    """
    all_statements = {}
    for user_id in user_ids:
        user_statements = {}
        for verb in VERBS:
            print(f"Fetching data for user {user_id} and verb {verb}...")
            statements = fetch_statements(user_id, verb)
            
            unique_statements = sort_and_deduplicate(statements)
            user_statements[verb] = unique_statements
            
            print(f"Processed {len(statements)} statements, deduplicated to {len(unique_statements)}")
            
        all_statements[user_id] = user_statements
    return all_statements


def sort_and_deduplicate(data):

    try:
        deduplicated_data = {item["timestamp"]: item for item in data}.values()

        sorted_data = sorted(deduplicated_data, key=lambda x: x["timestamp"])
        
        return sorted_data
    except Exception as e:
        print(f"Error during sorting and deduplication: {e}")
        return data  

def save_statements_to_json(data, filename="statements.json"):
    """
    Save the statements data to a JSON file.
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Statements saved to {filename}")

def process_user_statements(user_ids, output_file="statements.json"):
    """
    Main function to process user statements.
    
    Args:
        user_ids (list): List of user IDs to process.
        output_file (str): Path to save the resulting statements.
    """
    statements = download_statements(user_ids)
    save_statements_to_json(statements, output_file)
    print(f"Processing complete for users: {user_ids}")

# Example usage for external invocation
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python fetch_statements.py <output_file> <user_id_1> <user_id_2> ...")
        sys.exit(1)
    
    output_file = sys.argv[1]
    user_ids = sys.argv[2:]

    process_user_statements(user_ids, output_file)

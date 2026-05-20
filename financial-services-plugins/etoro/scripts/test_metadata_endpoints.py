import json
import uuid
import urllib.request
import os

def test_metadata():
    config_path = r"d:\Projects\Antigravity\Financial AI\financial-services-plugins\etoro\mcp\etoro.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    env = config.get("env", {})
    api_key = env.get("ETORO_API_KEY")
    user_key = env.get("ETORO_USER_API_KEY_DEMO")
    
    base_url = "https://public-api.etoro.com/api/v1"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "x-request-id": str(uuid.uuid4()),
        "x-api-key": api_key,
        "x-user-key": user_key,
        "Content-Type": "application/json"
    }

    test_id = 10881 # AMZN in the user's screenshot? No, AMZN is usually a specific ID.
    
    endpoints = [
        f"{base_url}/metadata/instrument?id={test_id}",
        f"{base_url}/metadata/instruments",
        f"{base_url}/market-data/instruments/{test_id}"
    ]
    
    results = {}
    for url in endpoints:
        print(f"Testing {url}...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                results[url] = json.loads(response.read().decode())
        except Exception as e:
            results[url] = str(e)
            
    with open("metadata_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    test_metadata()

import json
import uuid
import urllib.request
import urllib.error
import os

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

KEYRING_SERVICE = "antigravity_etoro"

def _load_credentials():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.abspath(os.path.join(script_dir, "..", "mcp", "etoro.json"))
    
    config_env = {}
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_env = json.load(f).get("env", {})
            
    creds = {}
    keys_to_load = ["ETORO_API_KEY", "ETORO_USER_API_KEY_REAL", "ETORO_USER_API_KEY_DEMO"]

    if KEYRING_AVAILABLE:
        for k in keys_to_load:
            val = keyring.get_password(KEYRING_SERVICE, k)
            if val:
                creds[k] = val

    for k in keys_to_load:
        if k not in creds and config_env.get(k):
            creds[k] = config_env[k]

    return creds

def test_watchlists():
    creds = _load_credentials()
    api_key = creds.get("ETORO_API_KEY")
    user_key = creds.get("ETORO_USER_API_KEY_REAL")
    
    base_url = "https://public-api.etoro.com/api/v1"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "x-request-id": str(uuid.uuid4()),
        "x-api-key": api_key,
        "x-user-key": user_key,
        "Content-Type": "application/json"
    }

    # Possible watchlist endpoints:
    endpoints = [
        f"{base_url}/watchlists",
        f"{base_url}/watching/user/watchlists",
        f"https://www.etoro.com/api/sts/v2/watchlists"
    ]
    
    results = {}
    for url in endpoints:
        print(f"Testing {url}...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                try:
                    data = json.loads(response.read().decode())
                    results[url] = data
                    print(f"SUCCESS: Found data at {url}")
                except:
                    results[url] = "Non-JSON response"
        except urllib.error.HTTPError as e:
            results[url] = f"HTTP Error: {e.code}"
        except Exception as e:
            results[url] = str(e)
            
    with open("watchlist_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    test_watchlists()

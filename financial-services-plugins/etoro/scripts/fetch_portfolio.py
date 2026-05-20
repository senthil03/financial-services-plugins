import json
import uuid
import urllib.request
import urllib.error
import os
import sys

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

KEYRING_SERVICE = "antigravity_etoro"

def get_instrument_metadata():
    # Use path relative to script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_path = os.path.join(script_dir, "instruments_metadata.json")
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
            
    print("Downloading instrument metadata (approx 11MB)...")
    url = "https://api.etorostatic.com/sapi/instrumentsmetadata/V1.1/instruments"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            # Convert to a more efficient lookup map
            mapping = {
                str(item["InstrumentID"]): {
                    "symbol": item.get("SymbolFull", "N/A"),
                    "name": item.get("InstrumentDisplayName", "N/A")
                }
                for item in data.get("InstrumentDisplayDatas", [])
            }
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(mapping, f)
            return mapping
    except Exception as e:
        print(f"Error downloading metadata: {e}")
        return {}

def _load_credentials(config_env: dict) -> dict:
    """
    Load API credentials with priority:
      1. Windows Credential Manager (keyring) — most secure
      2. etoro.json env block — legacy fallback (warns if used)
    """
    creds = {}
    keys_to_load = ["ETORO_API_KEY", "ETORO_USER_API_KEY_REAL", "ETORO_USER_API_KEY_DEMO"]

    if KEYRING_AVAILABLE:
        for k in keys_to_load:
            val = keyring.get_password(KEYRING_SERVICE, k)
            if val:
                creds[k] = val

    # Fallback to JSON for any key not found in keyring
    missing_from_keyring = [k for k in keys_to_load if k not in creds]
    if missing_from_keyring:
        for k in missing_from_keyring:
            if config_env.get(k):
                creds[k] = config_env[k]
                print(f"  ⚠️  Warning: {k} loaded from plain-text etoro.json.")
                print("     Run setup_credentials.py to migrate to Windows Credential Manager.")

    return creds


def fetch_portfolio(arg_account_type=None):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.abspath(os.path.join(script_dir, "..", "mcp", "etoro.json"))

    # Load non-sensitive config (account type) from JSON
    config_env = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config_env = json.load(f).get("env", {})
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config file: {e}")
            return

    # Load credentials securely
    creds = _load_credentials(config_env)
    api_key = creds.get("ETORO_API_KEY")

    # Use provided argument or fall back to config default
    account_type = (arg_account_type or config_env.get("ETORO_ACCOUNT_TYPE", "real")).lower()

    # Pick the correct user key
    if account_type == "demo":
        user_key = creds.get("ETORO_USER_API_KEY_DEMO")
    else:
        user_key = creds.get("ETORO_USER_API_KEY_REAL")

    if not api_key or not user_key:
        print(f"Error: Credentials for '{account_type}' account not found.")
        print("  \u2192 Run: python setup_credentials.py")
        return
    
    base_url = "https://public-api.etoro.com/api/v1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "x-request-id": str(uuid.uuid4()),
        "x-api-key": api_key,
        "x-user-key": user_key,
        "Content-Type": "application/json"
    }

    def api_call(url):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            return {"error": str(e)}

    # 1. Fetch P&L and Positions
    print(f"Fetching {account_type} portfolio...")
    pnl_data = api_call(f"{base_url}/trading/info/{account_type}/pnl")
    
    positions = []
    if "clientPortfolio" in pnl_data and "positions" in pnl_data["clientPortfolio"]:
        positions = pnl_data["clientPortfolio"]["positions"]

    if not positions:
        print("No open positions found.")
        # Minimal result for empty portfolio
        result = {"account_type": account_type, "summary": [], "raw_pnl": pnl_data}
        result_path = os.path.join(script_dir, "portfolio_result.json")
        with open(result_path, "w") as f:
            json.dump(result, f, indent=2)
        return

    # 2. Map Instrument IDs to Symbols/Names
    print("Mapping assets...")
    metadata_map = get_instrument_metadata()

    # 3. Aggregate Positions
    asset_groups = {}
    for p in positions:
        iid = str(p["instrumentID"]) 
        if iid not in asset_groups:
            meta = metadata_map.get(iid, {"symbol": f"ID:{iid}", "name": "Unknown Asset"})
            asset_groups[iid] = {
                "instrumentID": iid,
                "symbol": meta["symbol"],
                "name": meta["name"],
                "units": 0.0,
                "total_cost": 0.0,
                "pnl": 0.0,
                "net_value": 0.0,
                "current_price": 0.0
            }
        
        g = asset_groups[iid]
        units = p.get("units", 0.0)
        open_rate = p.get("openRate", 0.0)
        pnl_val = p.get("unrealizedPnL", {}).get("pnL", 0.0)
        exposure = p.get("unrealizedPnL", {}).get("exposureInAccountCurrency", 0.0)
        close_rate = p.get("unrealizedPnL", {}).get("closeRate", 0.0)
        
        g["units"] += units
        g["total_cost"] += (units * open_rate)
        g["pnl"] += pnl_val
        g["net_value"] += exposure
        g["current_price"] = close_rate

    # Final calculations for table
    summary_table = []
    for iid, g in asset_groups.items():
        avg_open = g["total_cost"] / g["units"] if g["units"] > 0 else 0
        pnl_pct = (g["pnl"] / g["total_cost"] * 100) if g["total_cost"] > 0 else 0
        
        summary_table.append({
            "Asset": g["symbol"],
            "Name": g["name"],
            "Price": g["current_price"],
            "Units": round(g["units"], 6),
            "Avg Open": round(avg_open, 6),
            "P/L": round(g["pnl"], 2),
            "P/L (%)": f"{round(pnl_pct, 2)}%",
            "Net Value": round(g["net_value"], 2)
        })

    # Sort table by Net Value descending as in typical portfolio views
    summary_table.sort(key=lambda x: x["Net Value"], reverse=True)

    # 4. Save combined result
    result = {
        "account_type": account_type,
        "summary": summary_table,
        "raw_pnl": pnl_data,
        "total_unrealized_pnl": pnl_data.get("clientPortfolio", {}).get("unrealizedPnL", 0.0),
        "available_credit": pnl_data.get("clientPortfolio", {}).get("credit", 0.0)
    }
    
    result_path = os.path.join(script_dir, "portfolio_result.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    
    # Auto-sync to dashboard folder if it exists
    dashboard_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "..", "dashboard"))
    if os.path.exists(dashboard_dir):
        import shutil
        shutil.copy(result_path, os.path.join(dashboard_dir, "portfolio_result.json"))
        print(f"Synced latest data to dashboard.")

    print(f"Fetch complete for {account_type}. Aggregated {len(summary_table)} assets.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fetch_portfolio(sys.argv[1])
    else:
        fetch_portfolio()

import json
import os
import sys
import urllib.request
from datetime import datetime
from email.header import Header

# Path Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PORTFOLIO_PATH = os.path.join(SCRIPT_DIR, "portfolio_result.json")
BASELINE_PATH = os.path.join(SCRIPT_DIR, "alerts_baseline_prices.json")
LOG_PATH = r"d:\Projects\Antigravity\Financial AI\Reports\REGULATORY_ALERTS.log"

CHANNEL_ID = "senthil-portfolio-alerts-a8f4c2d9e1b7"

# Alert Thresholds
THRESHOLD_EQUITIES = 3.0       # Alert on +/- 3% moves
THRESHOLD_METALS = 1.5         # Alert on +/- 1.5% moves in Gold/Silver
SILVER_BUY_TARGET = 74.47      # Technical support re-entry trigger

# List of assets classified as precious metals
METAL_ASSETS = ["SILVER", "PPFB.DE"]

def log_alert(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as f:
        f.write(f"[{timestamp}] {level}: {message}\n")
    print(f"[{level}] {message}")

def send_push_notification(title, message, priority="default", tags="bell"):
    """Dispatches push notifications to ntfy.sh securely."""
    url = f"https://ntfy.sh/{CHANNEL_ID}"
    
    # Encode the title using RFC 2047 to support emojis and non-ASCII chars
    encoded_title = Header(title, 'utf-8').encode()
    
    headers = {
        "Title": encoded_title,
        "Priority": priority,
        "Tags": tags
    }
    req = urllib.request.Request(
        url,
        data=message.encode('utf-8'),
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as response:
            return True
    except Exception as e:
        log_alert(f"Failed to send push alert: {str(e)}", level="ERROR")
        return False

def load_portfolio_data():
    """Forces a refresh by calling fetch_portfolio first, then reading the JSON result."""
    try:
        # Import fetch_portfolio dynamically
        sys.path.append(SCRIPT_DIR)
        import fetch_portfolio
        fetch_portfolio.fetch_portfolio()
        
        if os.path.exists(PORTFOLIO_PATH):
            with open(PORTFOLIO_PATH, "r") as f:
                return json.load(f)
    except Exception as e:
        log_alert(f"Error refreshing portfolio: {str(e)}", level="ERROR")
    return None

def check_market_volatility():
    log_alert("Initializing Market Volatility & Commodity scan...")
    
    # 1. Fetch fresh price data
    portfolio_data = load_portfolio_data()
    if not portfolio_data or "summary" not in portfolio_data:
        log_alert("Failed to load portfolio summary. Aborting scan.", level="ERROR")
        return
        
    summary = portfolio_data["summary"]
    
    # 2. Load previous price baselines
    baselines = {}
    if os.path.exists(BASELINE_PATH):
        try:
            with open(BASELINE_PATH, "r") as f:
                baselines = json.load(f)
        except Exception:
            pass
            
    updated_baselines = {}
    triggered_alerts = []

    # 3. Analyze each asset in the portfolio
    for asset_data in summary:
        symbol = asset_data["Asset"]
        name = asset_data["Name"]
        current_price = asset_data["Price"]
        
        # Save current price for the next baseline run
        updated_baselines[symbol] = current_price
        
        # If no baseline exists, set it and skip this alert check
        if symbol not in baselines:
            continue
            
        baseline_price = baselines[symbol]
        if baseline_price <= 0:
            continue
            
        # Calculate percentage change
        pct_change = ((current_price - baseline_price) / baseline_price) * 100
        abs_change = abs(pct_change)
        
        # Determine threshold based on asset type
        is_metal = symbol in METAL_ASSETS
        threshold = THRESHOLD_METALS if is_metal else THRESHOLD_EQUITIES
        
        # A. Volatility Check (Big rise or drop)
        if abs_change >= threshold:
            direction = "Spike" if pct_change > 0 else "Drop"
            emoji = "🚀" if pct_change > 0 else "🚨"
            tags = "rocket,chart_with_upwards_trend" if pct_change > 0 else "chart_with_downwards_trend,warning"
            priority = "high" if abs_change >= (threshold * 1.5) else "default"
            
            title = f"{emoji} {symbol} Price {direction} Alert!"
            message = (
                f"{name} ({symbol}) has moved {round(pct_change, 2)}% in the latest session!\n"
                f"• Baseline Price: ${round(baseline_price, 4)}\n"
                f"• Current Price: ${round(current_price, 4)}\n"
                f"• Target Threshold: {threshold}%\n\n"
                f"Navigate to your dashboard to review allocation strategy."
            )
            triggered_alerts.append((title, message, priority, tags))
            
        # B. Special Precious Metals Trigger: Silver Target entry check
        if symbol == "SILVER" and current_price <= SILVER_BUY_TARGET:
            # Only trigger a buy-alert if it recently dipped below the target
            if baseline_price > SILVER_BUY_TARGET:
                title = "🪙 Silver Support Reached: BUY SIGNAL"
                message = (
                    f"Silver has dipped to ${current_price} (below your tactical re-entry support of ${SILVER_BUY_TARGET}!).\n"
                    f"Cost-averaging at this level matches your high-conviction hardware hedge strategy."
                )
                triggered_alerts.append((title, message, "high", "coin,direct_hit"))
                
    # 4. Save updated baselines
    with open(BASELINE_PATH, "w") as f:
        json.dump(updated_baselines, f, indent=2)
        
    # 5. Dispatch triggered alerts
    if triggered_alerts:
        log_alert(f"Dispatched {len(triggered_alerts)} price alerts!")
        for title, message, priority, tags in triggered_alerts:
            send_push_notification(title, message, priority, tags)
    else:
        log_alert("No asset volatility or entry triggers breached in this scan.")

if __name__ == "__main__":
    check_market_volatility()

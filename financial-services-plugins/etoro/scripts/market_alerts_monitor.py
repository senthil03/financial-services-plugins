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

def check_portfolio_equity_alerts(portfolio_data):
    """Monitors the total account equity and alerts if it reaches a new daily low."""
    try:
        available_credit = portfolio_data.get("available_credit", 0.0)
        summary = portfolio_data.get("summary", [])
        total_assets_val = sum(asset_data.get("Net Value", 0.0) for asset_data in summary)
        total_equity = round(available_credit + total_assets_val, 2)
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        tracking_path = os.path.join(SCRIPT_DIR, "daily_equity_tracking.json")
        
        # Load or initialize tracking
        tracking = {}
        if os.path.exists(tracking_path):
            try:
                with open(tracking_path, "r") as f:
                    tracking = json.load(f)
            except Exception:
                pass
                
        # Check if we transitioned to a new day
        if tracking.get("date") != current_date:
            tracking = {
                "date": current_date,
                "daily_open": total_equity,
                "daily_low": total_equity,
                "last_alerted_low": total_equity,
                "last_equity": total_equity
            }
            log_alert(f"New day initialized for equity tracking: Open = ${total_equity}")
            with open(tracking_path, "w") as f:
                json.dump(tracking, f, indent=2)
            return

        daily_open = tracking.get("daily_open", total_equity)
        daily_low = tracking.get("daily_low", total_equity)
        last_alerted_low = tracking.get("last_alerted_low", total_equity)
        
        # If current equity is lower than the daily low, check if we should alert
        if total_equity < daily_low:
            # Set a threshold of 0.25% drop from the last alerted low to avoid spam
            threshold_value = last_alerted_low * 0.9975
            
            if total_equity <= threshold_value or total_equity < daily_low * 0.9975:
                drop_from_open = round(((daily_open - total_equity) / daily_open) * 100, 2)
                
                title = "🔻 New Daily Equity Low Alert!"
                message = (
                    f"Your total portfolio equity has reached a new low for today!\n"
                    f"• Current Equity: ${total_equity:,}\n"
                    f"• Daily Open: ${daily_open:,}\n"
                    f"• Daily Low: ${total_equity:,}\n"
                    f"• Change from Open: -{drop_from_open}%\n\n"
                    f"Navigate to your dashboard to review allocation strategy."
                )
                
                send_push_notification(title, message, priority="high", tags="chart_with_downwards_trend,warning")
                log_alert(f"Alert sent: New daily equity low of ${total_equity} (dropped {drop_from_open}% from open)")
                
                tracking["last_alerted_low"] = total_equity
                
            tracking["daily_low"] = total_equity
            
        tracking["last_equity"] = total_equity
        with open(tracking_path, "w") as f:
            json.dump(tracking, f, indent=2)
            
    except Exception as e:
        log_alert(f"Error checking portfolio equity alerts: {str(e)}", level="ERROR")

def check_individual_shares_alerts(portfolio_data):
    """Monitors each individual stock in the portfolio and alerts if it reaches a new daily low."""
    try:
        summary = portfolio_data.get("summary", [])
        current_date = datetime.now().strftime("%Y-%m-%d")
        tracking_path = os.path.join(SCRIPT_DIR, "daily_shares_tracking.json")
        
        # Load or initialize tracking
        tracking = {}
        if os.path.exists(tracking_path):
            try:
                with open(tracking_path, "r") as f:
                    tracking = json.load(f)
            except Exception:
                pass
                
        # If new day, reset tracking for all assets
        if tracking.get("date") != current_date:
            assets_tracking = {}
            for asset_data in summary:
                symbol = asset_data["Asset"]
                price = asset_data["Price"]
                if price <= 0:
                    continue
                assets_tracking[symbol] = {
                    "daily_open": price,
                    "daily_low": price,
                    "last_alerted_low": price
                }
            tracking = {
                "date": current_date,
                "assets": assets_tracking
            }
            log_alert("New day initialized for individual shares tracking.")
            with open(tracking_path, "w") as f:
                json.dump(tracking, f, indent=2)
            return

        assets_tracking = tracking.get("assets", {})
        updated = False
        
        for asset_data in summary:
            symbol = asset_data["Asset"]
            name = asset_data["Name"]
            price = asset_data["Price"]
            
            if price <= 0:
                continue
                
            # If asset is new to tracking, initialize it
            if symbol not in assets_tracking:
                assets_tracking[symbol] = {
                    "daily_open": price,
                    "daily_low": price,
                    "last_alerted_low": price
                }
                updated = True
                continue
                
            asset_track = assets_tracking[symbol]
            daily_open = asset_track.get("daily_open", price)
            daily_low = asset_track.get("daily_low", price)
            last_alerted_low = asset_track.get("last_alerted_low", price)
            
            # If current price is lower than the recorded daily low
            if price < daily_low:
                # Set a threshold of 0.5% drop from the last alerted low to avoid spam
                threshold_value = last_alerted_low * 0.995
                
                if price <= threshold_value or price < daily_low * 0.995:
                    drop_from_open = round(((daily_open - price) / daily_open) * 100, 2)
                    
                    title = f"📉 {symbol} New Daily Low Alert!"
                    message = (
                        f"Share Alert: {name} ({symbol}) has reached a new low for today!\n"
                        f"• Current Price: ${round(price, 4)}\n"
                        f"• Daily Open: ${round(daily_open, 4)}\n"
                        f"• Change from Open: -{drop_from_open}%\n\n"
                        f"Tracked support levels and limit orders remain active."
                    )
                    
                    send_push_notification(title, message, priority="high", tags="chart_with_downwards_trend,warning")
                    log_alert(f"Alert sent: {symbol} reached new daily low of ${price} (down {drop_from_open}% from open)")
                    
                    asset_track["last_alerted_low"] = price
                    
                asset_track["daily_low"] = price
                updated = True
                
        if updated:
            tracking["assets"] = assets_tracking
            with open(tracking_path, "w") as f:
                json.dump(tracking, f, indent=2)
                
    except Exception as e:
        log_alert(f"Error checking individual shares alerts: {str(e)}", level="ERROR")

def check_market_volatility():
    log_alert("Initializing Market Volatility & Commodity scan...")
    
    # 1. Fetch fresh price data
    portfolio_data = load_portfolio_data()
    if not portfolio_data or "summary" not in portfolio_data:
        log_alert("Failed to load portfolio summary. Aborting scan.", level="ERROR")
        return
        
    # Run account equity and individual share checks
    check_portfolio_equity_alerts(portfolio_data)
    check_individual_shares_alerts(portfolio_data)
        
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

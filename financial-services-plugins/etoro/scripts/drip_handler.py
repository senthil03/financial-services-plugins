import json
import os
import sys
import subprocess
from datetime import datetime

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def run_fetch():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fetch_script = os.path.join(script_dir, "fetch_portfolio.py")
    subprocess.run([sys.executable, fetch_script], capture_output=True)

def send_windows_toast(title, message):
    # Uses a PowerShell one-liner to send a native Windows 10/11 notification
    ps_cmd = f"New-BurntToastNotification -Text '{title}', '{message}'"
    # Note: BurntToast is a popular module, but fallback to simple Script if not present
    fallback_ps = f'[Window.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; ' \
                  f'$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); ' \
                  f'$textNodes = $template.GetElementsByTagName("text"); ' \
                  f'$textNodes.Item(0).AppendChild($template.CreateTextNode("{title}")) | Out-Null; ' \
                  f'$textNodes.Item(1).AppendChild($template.CreateTextNode("{message}")) | Out-Null; ' \
                  f'$toast = [Windows.UI.Notifications.ToastNotification]::new($template); ' \
                  f'[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("{title}").Show($toast);'
    
    subprocess.run(["powershell", "-Command", fallback_ps], capture_output=True)

def log_alert(message):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(script_dir, "ALERTS.log")
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().isoformat()}] ALERT: {message}\n")
    print(f"!!! ALERT !!! {message}")
    send_windows_toast("Antigravity Portfolio Alert", message)

def run_reconciliation():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Update Portfolio Data
    old_portfolio = load_json(os.path.join(script_dir, "portfolio_result.json"))
    run_fetch()
    new_portfolio = load_json(os.path.join(script_dir, "portfolio_result.json"))
    
    if not old_portfolio or not new_portfolio:
        return

    # 2. Check for Order Fills (Alert Logic)
    old_orders = {o["orderID"]: o for o in old_portfolio.get("raw_pnl", {}).get("clientPortfolio", {}).get("orders", [])}
    new_orders = {o["orderID"]: o for o in new_portfolio.get("raw_pnl", {}).get("clientPortfolio", {}).get("orders", [])}
    
    # Monitored Targets
    monitored = {1004: "MSFT", 10836: "JEPQ"}

    for oid, o in old_orders.items():
        if oid not in new_orders:
            iid = o.get("instrumentID")
            if iid in monitored:
                asset_name = monitored[iid]
                log_alert(f"ORDER FILLED: {asset_name} at deep-buy target. Your income/growth position is now LIVE.")

    # 3. Dividend Logic (Plan B)
    # Re-using the logic from v2 here...
    history = load_json(os.path.join(script_dir, "balance_history.json"))
    if history:
        current_credit = new_portfolio.get("available_credit", 0.0)
        last_credit = history.get("last_credit", 0.0)
        if (current_credit - last_credit) > 1.00:
            # (Matches with Calendar logic here)
            pass
        history["last_credit"] = current_credit
        with open(os.path.join(script_dir, "balance_history.json"), "w") as f:
            json.dump(history, f, indent=2)

if __name__ == "__main__":
    run_reconciliation()

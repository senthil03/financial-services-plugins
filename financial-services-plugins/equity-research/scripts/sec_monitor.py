import urllib.request
import json
import time
from datetime import datetime
import sys

# SEC requires a user-agent in a specific format: CompanyName ContactEmail
USER_AGENT = "Antigravity_Financial_AI support@example.com"

TICKER_TO_CIK = {
    "IONQ": "0001828064",
    "SKYT": "0001814329" 
}

def check_recent_filings(ticker, target_form="S-4"):
    cik = TICKER_TO_CIK.get(ticker.upper())
    if not cik:
        print(f"Error: CIK for {ticker} not found in dictionary.")
        return False
        
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
        
        filings = data.get("filings", {}).get("recent", {})
        if not filings:
            print("No recent filings found.")
            return False
            
        forms = filings.get("form", [])
        dates = filings.get("filingDate", [])
        accessions = filings.get("accessionNumber", [])
        
        print(f"--- Recent Filings for {ticker.upper()} ---")
        found_target = False
        
        for i in range(min(15, len(forms))):
            form_type = forms[i]
            filing_date = dates[i]
            acc_num = accessions[i].replace("-", "")
            
            print(f"[{filing_date}] Form: {form_type}")
            
            if target_form in form_type:
                found_target = True
                link = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_num}/"
                print(f"\n🚨 ALERT: Targeted Form {target_form} FOUND! 🚨")
                print(f"Date: {filing_date}")
                print(f"Link: {link}\n")
                
        if not found_target:
            print(f"\nTarget Form '{target_form}' has NOT been filed recently.")
            return False
            
        return found_target
        
    except Exception as e:
        print(f"Error fetching data from SEC: {e}")
        return False

if __name__ == "__main__":
    ticker = "IONQ" if len(sys.argv) < 2 else sys.argv[1]
    form = "S-4" if len(sys.argv) < 3 else sys.argv[2]
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking EDGAR for {ticker} '{form}' filing...")
    check_recent_filings(ticker, form)

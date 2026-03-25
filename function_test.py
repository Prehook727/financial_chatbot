import yfinance as yf

def get_realtime_risk_data():
    """✅ The most stable version: capture risk core data in real time"""
    #Yahoo Standard Target Code
    tickers = {
        "VIX panic index": "^VIX",
        "Gold": "GC=F",
        "Crude oil": "CL=F",
        "S&P 500": "^GSPC"
    }

    result = {}
    for name, ticker in tickers.items():
        try:
            stock = yf.Ticker(ticker)
            # Get real-time current price
            price = stock.info.get("regularMarketPrice")
            result[name] = round(price, 2) if price else "Unavailable"
        except Exception as e:
            print(f"❌ {name} failed to obtain: {str(e)[:30]}")
            result[name] = "Unavailable"
    return f"""
Real-Time Risk Indicators:
- VIX (Fear Index): {result['VIX panic index']}
- Gold (Safe Haven): {result['Gold']}
- WTI Crude Oil: {result['Crude oil']}
- S&P 500: {result['S&P 500']}

Based on THESE REAL-TIME DATA, calculate MACRO RISK SCORE (0-100) and give a short English analysis.
Output format strictly:
RISK SCORE: X/100 (LEVEL: LOW/MEDIUM/HIGH)
Analysis: 1-2 short sentences.
"""

# test
if __name__ == "__main__":
    data = get_realtime_risk_data()
    print(data)
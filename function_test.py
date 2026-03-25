import yfinance as yf
import requests
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


def fetch_ticker_data(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d"
        res = requests.get(url, timeout=10)
        data = res.json()["chart"]["result"][0]
        meta = data["meta"]
        price = round(meta["regularMarketPrice"], 2)
        prev = round(meta["previousClose"], 2)
        chg = round(price - prev, 2)
        pct = round(chg / prev * 100, 2)
        return {"price": price, "chg": chg, "pct": pct}
    except Exception as e:
        return {"price": "N/A", "chg": 0, "pct": 0}

def get_industry_realtime_data():
    industries = {
        "Technology (XLK)": fetch_ticker_data("XLK"),
        "Energy (XLE)": fetch_ticker_data("XLE"),
        "Financial (XLF)": fetch_ticker_data("XLF"),
        "Healthcare (XLV)": fetch_ticker_data("XLV"),
        "Precious Metals (GLD)": fetch_ticker_data("GLD"),
        "Base Metals (XME)": fetch_ticker_data("XME"),
        "Defense (XAR)": fetch_ticker_data("XAR")
    }

    lines = ["Real-Time Industry ETF Performance:"]
    for name, dt in industries.items():
        lines.append(f"- {name}: ${dt['price']} ({dt['pct']}%)")
    return "\n".join(lines)
# test
if __name__ == "__main__":
    data = get_industry_realtime_data()
    print(data + """
You are a professional industry rotation analyst.
Based on REAL-TIME PRICE MOVEMENTS, analyze:
1. Top 2 Hot Industries
2. Driver: safe-haven / price surge / policy / risk appetite
3. Brief rotation conclusion

Reply ONLY in ENGLISH, concise, structured.
""")
import yfinance as yf


def get_price(ticker: str):
    try:
        tick = yf.Ticker(ticker)
        data = tick.history(period="1d", interval="1m")
        price = round(data["Close"].iloc[-1], 2)
        prev = round(data["Close"].iloc[0], 2)
        pct = round((price - prev) / prev * 100, 2)
        return {"price": price, "pct": pct}
    except Exception as e:
        return {"price": None, "pct": 0}
    
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

As a financial AI agent, based on these indicators above, calculate MACRO RISK SCORE (0-100) and give a short English analysis.
Output format strictly:
RISK SCORE: X/100 (LEVEL: LOW/MEDIUM/HIGH)
Analysis: 1-2 short sentences.
"""

async def get_industry():
    industries = {
        "XLK (Tech)": get_price("XLK"),
        "XLE (Energy)": get_price("XLE"),
        "XLF (Finance)": get_price("XLF"),
        "XLV (Healthcare)": get_price("XLV"),
        "GLD (Gold)": get_price("GLD"),
        "XAR (Defense)": get_price("XAR")
    }
    lines = [f"{n}: ${d['price']} ({d['pct']}%)" for n, d in industries.items() if d['price']]
    prompt = "\n".join(lines) + """
Analyze industry rotation.
Output TOP 2 hot industries + driver + 1-line conclusion.
"""
    return prompt
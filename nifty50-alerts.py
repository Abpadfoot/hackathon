import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# Nifty 50 stock symbols on Yahoo Finance (suffix .NS for NSE)
nifty_50 = [
    "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS",
    "BAJFINANCE.NS", "BAJAJFINSV.NS", "BHARTIARTL.NS", "BPCL.NS", "BRITANNIA.NS",
    "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS", "EICHERMOT.NS",
    "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS",
    "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "INDUSINDBK.NS", "INFY.NS",
    "ITC.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LTIM.NS", "LT.NS",
    "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS", "ONGC.NS",
    "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SHREECEM.NS",
    "SUNPHARMA.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TCS.NS",
    "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS", "UPL.NS", "WIPRO.NS"
]

# nifty_50 = ["HINDUNILVR.NS"]

# EMA periods to track
ema_periods = [20, 50, 89, 200]
threshold_pct = 10.0  # price within ±1%

# Slack webhook URL (replace this with your real webhook URL)
SLACK_WEBHOOK = "https://hooks.slack.com/services/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"

def fetch_ema_alerts(symbol, interval):
    try:
        df = yf.download(symbol, period='max', interval=interval, auto_adjust=True, progress=False)
        if df.empty or len(df) < max(ema_periods):
            return []

        for period in ema_periods:
            df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()

        latest_row = df.iloc[-1]
        price = float(latest_row['Close'])

        alerts = []
        for period in ema_periods:
            ema = float(latest_row[f'EMA_{period}'])
            diff_pct = abs(price - ema) / ema * 100
            if diff_pct <= threshold_pct:
                alerts.append(
                    f"{symbol} is near {period} EMA on {interval.upper()} chart (Price: {price:.2f}, EMA: {ema:.2f}, Diff={diff_pct:.2f}%)"
                )

        return alerts
    except Exception as e:
        print(f"Error processing {symbol} on {interval} chart: {e}")
        return []


def send_slack_message(text):
    payload = {"text": text}
    try:
        requests.post(SLACK_WEBHOOK, json=payload)
    except Exception as e:
        print(f"Slack send failed: {e}")

def main():
    all_alerts = []

    for symbol in nifty_50:
        print(f"Checking {symbol}...")
        # daily_alerts = fetch_ema_alerts(symbol, '1d')
        weekly_alerts = fetch_ema_alerts(symbol, '1wk')
        # all_alerts.extend(daily_alerts + weekly_alerts)
        all_alerts.extend( weekly_alerts)

    if all_alerts:
        msg = f"*EMA Alert — {datetime.now().strftime('%Y-%m-%d %H:%M')}* 📈\n\n" + "\n".join(all_alerts)
        send_slack_message(msg)
    else:
        print("No alerts today.")

if __name__ == "__main__":
    main()

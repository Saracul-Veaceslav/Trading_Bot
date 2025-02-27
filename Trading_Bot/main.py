import ccxt
import os
import time
import pandas as pd
from dotenv import load_dotenv
from strategies.sma_strategy import simple_moving_average

# ✅ Load API Keys
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_SECRET_KEY")

# ✅ Connect to Binance
exchange = ccxt.binance({
    "apiKey": API_KEY,
    "secret": API_SECRET,
    "options": {"defaultType": "spot"},  # Spot trading
})

# ✅ Function to Fetch Market Data
def fetch_market_data(symbol="BTC/USDT", timeframe="1m", limit=100):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    data = [[candle[0], candle[4]] for candle in ohlcv]  # Get timestamps & close prices
    return data

# ✅ Function to Place Orders
def place_order(symbol, side, amount):
    try:
        order = exchange.create_market_order(symbol, side, amount)
        print(f"✅ Placed {side.upper()} order for {amount} {symbol} at market price!")
    except Exception as e:
        print(f"❌ Error placing order: {e}")

# ✅ Trading Loop (Runs Forever)
print("🚀 Trading bot started. Press Ctrl+C to stop.")
while True:
    try:
        market_data = fetch_market_data()
        df = simple_moving_average(market_data)
        latest_signal = df.iloc[-1]['signal']

        # ✅ Execute Trades Based on Signals
        if latest_signal == 1:
            place_order("BTC/USDT", "buy", 0.001)  # Adjust amount
        elif latest_signal == -1:
            place_order("BTC/USDT", "sell", 0.001)
        else:
            print("📉 No trade signal, waiting...")

        # ✅ Print last few rows of data for debugging
        print(df.tail(5))

        # ✅ Sleep for 60 seconds before checking again
        time.sleep(60)

    except Exception as e:
        print(f"⚠️ Error in loop: {e}")
        time.sleep(5)  # Wait before retrying

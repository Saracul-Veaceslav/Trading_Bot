import backtrader as bt
import pandas as pd
import ccxt

# ✅ Step 1: Define Your Strategy
class SMAStrategy(bt.Strategy):
    params = (("short_window", 10), ("long_window", 50))

    def __init__(self):
        self.sma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_window)
        self.sma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_window)

    def next(self):
        if self.sma_short[0] > self.sma_long[0] and not self.position:
            self.buy()
            print(f"📈 BUY: {self.data.datetime.date(0)} at {self.data.close[0]}")
        elif self.sma_short[0] < self.sma_long[0] and self.position:
            self.sell()
            print(f"📉 SELL: {self.data.datetime.date(0)} at {self.data.close[0]}")

# ✅ Step 2: Fetch Historical Data
def fetch_historical_data(symbol="BTC/USDT", timeframe="1h", limit=1000):
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    df = pd.DataFrame(ohlcv, columns=["datetime", "open", "high", "low", "close", "volume"])
    df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")
    df.set_index("datetime", inplace=True)
    return df

# ✅ Step 3: Convert Data for Backtrader
def run_backtest():
    df = fetch_historical_data()
    data_feed = bt.feeds.PandasData(dataname=df)

    # ✅ Step 4: Set Up Backtrader
    cerebro = bt.Cerebro()
    cerebro.addstrategy(SMAStrategy)
    cerebro.adddata(data_feed)
    cerebro.broker.set_cash(10000)  # Starting Capital
    cerebro.broker.setcommission(commission=0.001)  # Exchange Fee
    cerebro.run()
    cerebro.plot()

if __name__ == "__main__":
    run_backtest()

import pandas as pd

def simple_moving_average(data, short_window=10, long_window=50):
    """
    Compute short and long SMA and generate buy/sell signals.
    """
    df = pd.DataFrame(data, columns=['timestamp', 'price'])
    df['SMA_short'] = df['price'].rolling(window=short_window).mean()
    df['SMA_long'] = df['price'].rolling(window=long_window).mean()

    df['signal'] = 0
    df.loc[df['SMA_short'] > df['SMA_long'], 'signal'] = 1  # Buy
    df.loc[df['SMA_short'] < df['SMA_long'], 'signal'] = -1  # Sell

    return df

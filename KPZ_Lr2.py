import pandas as pd
from binance.client import Client

# Функція для отримання історичних даних про торги з Binance
def get_historical_data(symbol, start_str, end_str, interval='1m'):
    # Створення клієнта API
    client = Client()
    # Мапа для інтервалів часу
    interval_map = {
        '1m': Client.KLINE_INTERVAL_1MINUTE,
        # Додайте інші інтервали за потребою
    }
    # Отримання даних
    klines = client.get_historical_klines(symbol, interval_map.get(interval, interval), start_str, end_str)

    # Створення DataFrame
    columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
               'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
               'taker_buy_quote_asset_volume', 'ignore']
    df = pd.DataFrame(klines, columns=columns)

    # Конвертація даних
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    df['time'] = pd.to_datetime(df['time'], unit='ms')

    return df

# Функція для розрахунку індексу відносної сили (RSI)
def calculate_RSI(df, period=14):
    delta = df['close'].diff()
    gain = (delta > 0) * delta
    loss = (delta < 0) * -delta

    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    df[f'RSI_{period}'] = rsi
    return df[['time', f'RSI_{period}']]

# Приклад використання
symbol = 'BTCUSDT'
start_time = (pd.Timestamp.now() - pd.Timedelta(days=1)).strftime('%Y-%m-%d %H:%M')
end_time = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')

data = get_historical_data(symbol, start_time, end_time)
rsi_data = calculate_RSI(data)

print(rsi_data.tail())

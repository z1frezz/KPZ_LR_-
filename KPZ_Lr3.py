import datetime
import pandas as pd
from binance.client import Client
import pandas_ta as ta

# Конфігурація
SYMBOL = "BTCUSDT"
INTERVAL = Client.KLINE_INTERVAL_1MINUTE
N_DAYS_AGO = 1

def fetch_historical_data(symbol, interval, start_str, end_str):
    client = Client()
    klines = client.get_historical_klines(symbol, interval, start_str, end_str)
    columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
               'quote_vol', 'trades', 'tb_base_vol', 'tb_quote_vol', 'ignore']
    df = pd.DataFrame(klines, columns=columns)
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    return df[['time', *numeric_cols]]

def apply_technical_indicators(df):
    df.ta.rsi(append=True)
    df.ta.cci(append=True)
    df.ta.macd(close='close', append=True)
    return df.dropna()

def interpret_signals(df):
    df['RSI_Signal'] = df['RSI_14'].apply(lambda x: "перекупленість" if x > 70 else "перепроданість" if x < 30 else "нейтрально")
    df['CCI_Signal'] = df['CCI_14_0.015'].apply(lambda x: "можливий початок висхідного тренду" if x < -100 else "можливий початок низхідного тренду" if x > 100 else "нейтрально")
    df['MACD_Signal'] = df.apply(lambda row: "бичачий перехрест" if row['MACD_12_26_9'] > row['MACDs_12_26_9'] else "ведмежий перехрест" if row['MACD_12_26_9'] < row['MACDs_12_26_9'] else "нейтрально", axis=1)
    return df

def main():
    start_date = (datetime.datetime.now() - datetime.timedelta(days=N_DAYS_AGO)).strftime('%Y-%m-%d %H:%M')
    end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    data = fetch_historical_data(SYMBOL, INTERVAL, start_date, end_date)
    data_with_indicators = apply_technical_indicators(data)
    data_with_signals = interpret_signals(data_with_indicators)
    data_with_signals.to_csv('prediction.csv', index=False)
    print("Saved predictions to prediction.csv")

if __name__ == "__main__":
    main()

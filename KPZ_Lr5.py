import pandas as pd
import matplotlib.pyplot as plt
from binance import Client
from dataclasses import dataclass
import ta


@dataclass
class Signal:
    time: pd.Timestamp
    asset: str
    quantity: float
    side: str
    entry: float
    take_profit: float
    stop_loss: float
    result: float = None


def fetch_data(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_1MINUTE, start_str="1 week ago UTC", end_str="now UTC"):
    client = Client()
    k_lines = client.get_historical_klines(symbol, interval, start_str, end_str)
    columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume',
               'Number of Trades', 'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore']
    df = pd.DataFrame(k_lines, columns=columns)
    df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)
    return df


def calculate_indicators(df):
    df['ADX'] = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close'], window=14).adx()
    df['CCI'] = ta.trend.CCIIndicator(df['High'], df['Low'], df['Close'], window=20).cci()
    return df


def generate_signals(df):
    signals = []
    for index, row in df.iterrows():
        signal = None
        if row['CCI'] < -100 and row['ADX'] > 25:
            signal = 'sell'
        elif row['CCI'] > 100 and row['ADX'] > 25:
            signal = 'buy'

        if signal:
            stop_loss_price = round((1 - 0.02) * row['Close'], 1) if signal == "buy" else round(
                (1 + 0.02) * row['Close'], 1)
            take_profit_price = round((1 + 0.1) * row['Close'], 1) if signal == "buy" else round(
                (1 - 0.1) * row['Close'], 1)
            signals.append(
                Signal(row['Time'], 'BTCUSDT', 100, signal, row['Close'], take_profit_price, stop_loss_price))
    return signals


def plot_signals(df, signals):
    plt.figure(figsize=(14, 7))
    plt.plot(df['Time'], df['Close'], label='Цена закрытия BTCUSDT')
    for signal in signals:
        plt.scatter(signal.time, signal.entry, color='green' if signal.side == 'buy' else 'red',
                    label=f'{signal.side.capitalize()} Signal at {signal.entry}', s=100)
    plt.title('Цена BTCUSDT и Торгові Сигнали')
    plt.xlabel('Час')
    plt.ylabel('Ціна')
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    data = fetch_data()
    data = calculate_indicators(data)
    signals = generate_signals(data)
    plot_signals(data, signals)

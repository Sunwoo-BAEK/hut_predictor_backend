import yfinance as yf
from tensorflow.keras.models import load_model
from datetime import datetime, timedelta
import joblib
import numpy as np
import pandas as pd

# Load once when the app starts
model = load_model("app/binaries/hut_model.h5")
scaler = joblib.load("app/binaries/hut_scaler.pkl")

def predict_price(hours: int) -> list:
    
    # Get data
    df_scaled = get_data()

    print("Data shape:", df_scaled.shape)

    X = create_sequence(df_scaled)

    print("Input shape:", X.shape)

    # Make predictions
    y_pred = model.predict(X)

    print("Predictions shape:", y_pred.shape)
    print("Predictions:", y_pred)

    # Create dummy array of same shape expected by scaler
    padded = np.zeros((21, 8))  # 21 samples, 8 features
    padded[:, 0] = y_pred.reshape(-1)  # Assuming the target was at index 0

    # Inverse transform
    unscaled = scaler.inverse_transform(padded)

    # Extract only the column we care about (closing price)
    future_predictions = unscaled[:, 0]

    requested_predictions = future_predictions[:hours]

    # Get future market hours
    last_time = df_scaled.index[-1]
    future_times = get_future_market_hours(last_time, hours)

    future_prices = pd.DataFrame(requested_predictions, index=future_times, columns=["HUT_Close"])
    future_prices.index.name = "DateTime"
    future_prices.reset_index(inplace=True)
    future_prices["HUT_Close"] = future_prices["HUT_Close"].round(2)
    # future_prices["DateTime"] = future_prices["DateTime"].dt.strftime("%Y-%m-%d %H:%M:%S") # what does this do?

    print("Predictions:")
    print(future_prices.head(hours))

    return future_prices.to_dict(orient="records")

def create_sequence(data, lookback=56):
    return data.iloc[-lookback:].values.reshape(1, lookback, -1)

def get_future_market_hours(start_time: datetime, hours: int):
    future_times = []
    current = start_time

    while len(future_times) < hours:
        current += timedelta(hours=1)
        if current.weekday() < 5 and 14 <= current.hour <= 20:
            future_times.append(current)

    return future_times

def get_data():
    df_hut = yf.download("HUT", period="10d", interval="1h")
    df_btc = yf.download("BTC-USD", period="15d", interval="1h")
    df_hut.index = df_hut.index + pd.Timedelta(minutes=30) # shift to hourly to match with BTC

    # Rename for clarity before merge
    df_hut = df_hut.rename(columns=lambda x: f"HUT_{x}")
    df_btc = df_btc.rename(columns=lambda x: f"BTC_{x}")

    # Add BTC return/momentum features
    df_btc['BTC_return_1h'] = df_btc['BTC_Close'].pct_change(periods=1)
    df_btc['BTC_return_6h'] = df_btc['BTC_Close'].pct_change(periods=6)

    # Join only BTC columns we care about
    df = df_hut.join(df_btc, how='left')

    # Add Exponential Moving Averages (EMA)
    df['HUT_EMA_9'] = df['HUT_Close'].ewm(span=9, adjust=False).mean()
    df['BTC_EMA_9'] = df['BTC_Close'].ewm(span=9, adjust=False).mean()

    # Clean df
    df.dropna(inplace=True)
    df.columns = df.columns.get_level_values(0)  # gets rid of tickers row

    features = [
        'HUT_Close', 'HUT_Volume', 'HUT_EMA_9',
        'BTC_Close', 'BTC_Volume', 'BTC_return_1h',
        'BTC_return_6h', 'BTC_EMA_9'
    ]

    print("Data:")
    print(df.describe())

    df_scaled = pd.DataFrame(scaler.transform(df[features]), columns=features, index=df.index)

    return df_scaled

print(predict_price(21))
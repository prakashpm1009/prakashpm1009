import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
import pandas as pd
from utils.dhan_api import get_intraday_1min_data, get_daily_ohlcv_data
from config.watchlist_metadata import metadata_dict


def fetch_intraday_daily_data(stock_name, security_id, exchange_segment, instrument_type):
    """
    Fetches 1-minute intraday and daily OHLCV data for a stock using the DHAN API.

    Args:
        stock_name (str): Trading symbol (e.g. RELIANCE)
        security_id (int): Dhan security ID
        exchange_segment (str): e.g. "NSE_EQ", "BSE_EQ"
        instrument_type (str): e.g. "EQUITY"

    Returns:
        tuple: df (all intraday), df_today (latest day only), df_daily (1-year daily), latest_date
    """

    # ✅ Fetch intraday 1-minute OHLCV
    df = get_intraday_1min_data(
        security_id=security_id,
        exchange_segment=exchange_segment,
        instrument_type=instrument_type
    )

    if df is None or df.empty:
        print(f"⚠️ No intraday data for {stock_name}")
        return None, None, None, None

    # 🧼 Normalize and debug intraday DataFrame
    if 'startTime' in df.columns:
        df.rename(columns={'startTime': 'timestamp'}, inplace=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    print(f"📊 Intraday Columns: {df.columns.tolist()}")

    latest_date = df['date'].max()
    df_today = df[df['date'] == latest_date]

    # 🔍 Check row threshold (minimum candles)
    min_rows_required = 2 if datetime.now().time() <= datetime.strptime("09:20", "%H:%M").time() else 30
    if df_today.empty or df_today.shape[0] < min_rows_required:
        print(f"⚠️ Insufficient intraday data for {stock_name} (have {df_today.shape[0]}, need {min_rows_required})")
        return None, None, None, None

    print(f"✅ {stock_name}: {df_today.shape[0]} rows found for today")

    # 📅 Fetch daily OHLCV (365 days)
    df_daily = get_daily_ohlcv_data(
        security_id=security_id,
        exchange_segment=exchange_segment,
        instrument_type=instrument_type
    )

    if df_daily is None or df_daily.empty:
        print(f"⚠️ No daily OHLCV data for {stock_name}")
        return None, None, None, None

    if 'startTime' in df_daily.columns:
        df_daily.rename(columns={'startTime': 'timestamp'}, inplace=True)
    df_daily['timestamp'] = pd.to_datetime(df_daily['timestamp'])
    df_daily = df_daily[df_daily['timestamp'] >= pd.Timestamp.now() - pd.Timedelta(days=365)]
    print(f"📊 Daily Columns: {df_daily.columns.tolist()}")

    return df, df_today, df_daily, latest_date
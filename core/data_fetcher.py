import sys
import os
from datetime import datetime
import pandas as pd

# Make parent folder importable when executed as script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.dhan_api import get_intraday_1min_data, get_daily_ohlcv_data  # noqa: E402
from config.watchlist_metadata import metadata_dict  # noqa: E402

# -----------------------------------------------------------------------------
# Internal helpers
# -----------------------------------------------------------------------------

_CANDIDATE_TIME_COLS = [
    "timestamp",
    "startTime",
    "start_time",
    "time",
    "dateTime",
    "datetime",
    "date",
    "start_ts",
]

def _standardize_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    """Return DataFrame with a guaranteed `timestamp` column of dtype datetime.

    The Dhan API has evolved over time, so the time column name can vary. This
    helper looks for any known variations and renames the first match to
    ``timestamp``. If no candidate column is found, a ``KeyError`` is raised so
    the caller can handle it appropriately.
    """
    for col in _CANDIDATE_TIME_COLS:
        if col in df.columns:
            if col != "timestamp":
                df = df.rename(columns={col: "timestamp"})
            break
    else:
        raise KeyError(
            "No suitable timestamp column found in DataFrame. Columns present: "
            f"{df.columns.tolist()}"
        )

    # Convert to datetime if not already
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df

# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------

def fetch_intraday_daily_data(stock_name, security_id, exchange_segment, instrument_type):
    """Fetches intraday (1-min) and daily OHLCV data for *stock_name*.

    Returns:
        tuple: ``(df_intraday, df_today, df_daily, latest_date)`` where:
            df_intraday (pd.DataFrame | None): Full intraday history for last day.
            df_today (pd.DataFrame | None): Rows for *latest trading date* only.
            df_daily (pd.DataFrame | None): Daily OHLCV for last 365 days.
            latest_date (datetime.date | None): Most recent trading day.
    """

    # 1️⃣ Intraday 1-minute
    df = get_intraday_1min_data(
        security_id=security_id,
        exchange_segment=exchange_segment,
        instrument_type=instrument_type,
    )
    if df is None or df.empty:
        print(f"⚠️ No intraday data for {stock_name}")
        return None, None, None, None

    try:
        df = _standardize_timestamp(df)
    except KeyError as e:
        print(f"❌ {stock_name}: {e}")
        return None, None, None, None

    # Add date helper column
    df["date_only"] = df["timestamp"].dt.date

    latest_date = df["date_only"].max()
    df_today = df[df["date_only"] == latest_date]

    # Ensure sufficient candles (handle early-morning edge-case)
    min_rows_required = 2 if datetime.now().time() <= datetime.strptime("09:20", "%H:%M").time() else 30
    if df_today.empty or len(df_today.index) < min_rows_required:
        print(
            f"⚠️ Insufficient intraday data for {stock_name} (have {len(df_today.index)}, "
            f"need {min_rows_required})"
        )
        return None, None, None, None

    # 2️⃣ Daily OHLCV (1 year)
    df_daily = get_daily_ohlcv_data(
        security_id=security_id,
        exchange_segment=exchange_segment,
        instrument_type=instrument_type,
    )
    if df_daily is None or df_daily.empty:
        print(f"⚠️ No daily OHLCV data for {stock_name}")
        return None, None, None, None

    try:
        df_daily = _standardize_timestamp(df_daily)
    except KeyError as e:
        print(f"❌ {stock_name} (daily): {e}")
        return None, None, None, None

    df_daily = df_daily[df_daily["timestamp"] >= pd.Timestamp.now() - pd.Timedelta(days=365)]

    return df, df_today, df_daily, latest_date
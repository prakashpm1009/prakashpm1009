from __future__ import annotations

import os
import sys
import logging
from datetime import datetime, date
from typing import Optional, Tuple

import pandas as pd

# Ensure parent directory is on the PYTHONPATH so that sibling modules can be imported when executed as a script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.dhan_api import get_intraday_1min_data, get_daily_ohlcv_data  # type: ignore  # noqa: E402
from config.watchlist_metadata import metadata_dict  # type: ignore  # noqa: E402

__all__ = ["fetch_intraday_daily_data"]

# ----------------------------------------------------------------------------
# Logging configuration
# ----------------------------------------------------------------------------
logger = logging.getLogger(__name__)
if not logger.handlers:
    # If no handlers have been configured yet (e.g. library usage), attach a basic one.
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    )
    logger.addHandler(_handler)
    # Default log level can be overridden by the root logger in host applications.
    logger.setLevel(logging.INFO)

# ----------------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------------

def fetch_intraday_daily_data(
    stock_name: str,
    security_id: int,
    exchange_segment: str,
    instrument_type: str,
) -> Tuple[
    Optional[pd.DataFrame],
    Optional[pd.DataFrame],
    Optional[pd.DataFrame],
    Optional[date],
]:
    """Fetch 1-minute intraday and 1-year daily OHLCV data for the provided symbol.

    Parameters
    ----------
    stock_name : str
        Trading symbol (e.g. ``"RELIANCE"``).
    security_id : int
        Dhan security identifier.
    exchange_segment : str
        Exchange segment (e.g. ``"NSE_EQ"`` or ``"BSE_EQ"``).
    instrument_type : str
        Instrument type (e.g. ``"EQUITY"``).

    Returns
    -------
    tuple
        ``(df_intraday_all, df_intraday_today, df_daily, latest_date)`` where each
        element is a :class:`~pandas.DataFrame` or ``None`` if unavailable, and
        ``latest_date`` is a :class:`datetime.date` of the most recent trading
        day for which intraday data was returned.
    """

    # ---------------------------------------------------------------------
    # Intraday (1-minute) OHLCV
    # ---------------------------------------------------------------------
    df_intraday = get_intraday_1min_data(
        security_id=security_id,
        exchange_segment=exchange_segment,
        instrument_type=instrument_type,
    )

    if df_intraday is None or df_intraday.empty:
        logger.warning("No intraday data for %s", stock_name)
        return None, None, None, None

    # Normalise column naming so downstream code is stable regardless of API revs.
    if "startTime" in df_intraday.columns:
        df_intraday = df_intraday.rename(columns={"startTime": "timestamp"})

    # Ensure timestamp dtype is correct and create a convenience `date` column.
    df_intraday["timestamp"] = pd.to_datetime(df_intraday["timestamp"], utc=True, errors="coerce")
    df_intraday["date"] = df_intraday["timestamp"].dt.date

    logger.debug("Intraday columns: %s", df_intraday.columns.tolist())

    latest_date: date = df_intraday["date"].max()  # type: ignore[assignment]
    df_intraday_today = df_intraday[df_intraday["date"] == latest_date]

    # Determine minimum number of candles required depending on time of day.
    now_time = datetime.now().time()
    market_open_buffer = datetime.strptime("09:20", "%H:%M").time()
    min_rows_required = 2 if now_time <= market_open_buffer else 30

    if df_intraday_today.empty or len(df_intraday_today.index) < min_rows_required:
        logger.warning(
            "Insufficient intraday data for %s (have %s, need %s)",
            stock_name,
            len(df_intraday_today.index),
            min_rows_required,
        )
        return None, None, None, None

    logger.info("%s: %d intraday rows found for today", stock_name, len(df_intraday_today.index))

    # ---------------------------------------------------------------------
    # Daily OHLCV (365 days)
    # ---------------------------------------------------------------------
    df_daily = get_daily_ohlcv_data(
        security_id=security_id,
        exchange_segment=exchange_segment,
        instrument_type=instrument_type,
    )

    if df_daily is None or df_daily.empty:
        logger.warning("No daily OHLCV data for %s", stock_name)
        return None, None, None, None

    if "startTime" in df_daily.columns:
        df_daily = df_daily.rename(columns={"startTime": "timestamp"})

    df_daily["timestamp"] = pd.to_datetime(df_daily["timestamp"], utc=True, errors="coerce")

    # Limit to the last 365 calendar days
    one_year_ago = pd.Timestamp.utcnow().normalize() - pd.Timedelta(days=365)
    df_daily = df_daily[df_daily["timestamp"] >= one_year_ago]

    logger.debug("Daily columns: %s", df_daily.columns.tolist())

    return df_intraday, df_intraday_today, df_daily, latest_date
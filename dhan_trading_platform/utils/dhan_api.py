"""
DHAN API utility functions for fetching market data.
This module contains the core API interaction functions.
"""
import pandas as pd
from typing import Optional, Union


def get_intraday_1min_data(security_id: int, exchange_segment: str, instrument_type: str) -> Optional[pd.DataFrame]:
    """
    Fetch 1-minute intraday OHLCV data from DHAN API.
    
    Args:
        security_id (int): DHAN security identifier
        exchange_segment (str): Exchange segment (e.g., "NSE_EQ", "BSE_EQ")
        instrument_type (str): Instrument type (e.g., "EQUITY")
    
    Returns:
        pd.DataFrame: Intraday data with columns [startTime, open, high, low, close, volume]
                     Returns None if API call fails
    """
    # Placeholder implementation
    pass


def get_daily_ohlcv_data(security_id: int, exchange_segment: str, instrument_type: str) -> Optional[pd.DataFrame]:
    """
    Fetch daily OHLCV data from DHAN API for the last 365 days.
    
    Args:
        security_id (int): DHAN security identifier
        exchange_segment (str): Exchange segment (e.g., "NSE_EQ", "BSE_EQ")
        instrument_type (str): Instrument type (e.g., "EQUITY")
    
    Returns:
        pd.DataFrame: Daily data with columns [startTime, open, high, low, close, volume]
                     Returns None if API call fails
    """
    # Placeholder implementation
    pass
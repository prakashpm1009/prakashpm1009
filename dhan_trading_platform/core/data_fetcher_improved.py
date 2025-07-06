import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, time
import pandas as pd
import logging
from typing import Optional, Tuple, Dict, Any
from utils.dhan_api import get_intraday_1min_data, get_daily_ohlcv_data
from config.watchlist_metadata import metadata_dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dhan_data_fetcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataFetcherError(Exception):
    """Custom exception for data fetcher errors."""
    pass


class DhanDataFetcher:
    """
    Enhanced data fetcher for DHAN trading platform with improved error handling,
    logging, caching, and validation.
    """
    
    def __init__(self):
        self.market_open_time = time(9, 15)  # 9:15 AM
        self.early_trading_time = time(9, 20)  # 9:20 AM
        self.cache = {}
        
    def _validate_inputs(self, stock_name: str, security_id: int, 
                        exchange_segment: str, instrument_type: str) -> None:
        """Validate input parameters."""
        if not stock_name or not isinstance(stock_name, str):
            raise DataFetcherError("Invalid stock_name: must be a non-empty string")
        
        if not isinstance(security_id, int) or security_id <= 0:
            raise DataFetcherError("Invalid security_id: must be a positive integer")
            
        valid_exchanges = ["NSE_EQ", "BSE_EQ", "NSE_FO", "NSE_CD", "MCX_COM"]
        if exchange_segment not in valid_exchanges:
            raise DataFetcherError(f"Invalid exchange_segment: must be one of {valid_exchanges}")
            
        valid_instruments = ["EQUITY", "FUTURES", "OPTIONS", "COMMODITY"]
        if instrument_type not in valid_instruments:
            raise DataFetcherError(f"Invalid instrument_type: must be one of {valid_instruments}")
    
    def _normalize_dataframe(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Normalize DataFrame with consistent column names and data types."""
        if df is None or df.empty:
            return df
            
        # Standardize timestamp column
        if 'startTime' in df.columns:
            df = df.rename(columns={'startTime': 'timestamp'})
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Add date column for easier filtering
        df['date'] = df['timestamp'].dt.date
        
        # Ensure OHLCV columns are numeric
        ohlcv_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in ohlcv_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with NaN values in critical columns
        df = df.dropna(subset=['timestamp', 'close'])
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        logger.info(f"Normalized {data_type} DataFrame: {len(df)} rows, columns: {df.columns.tolist()}")
        return df
    
    def _get_min_rows_required(self) -> int:
        """Calculate minimum rows required based on current time."""
        current_time = datetime.now().time()
        
        if current_time <= self.early_trading_time:
            return 2  # Very early in trading session
        elif current_time <= time(10, 0):
            return 15  # First hour of trading
        elif current_time <= time(12, 0):
            return 30  # Morning session
        else:
            return 50  # Full trading session
    
    def _filter_today_data(self, df: pd.DataFrame, stock_name: str) -> Optional[pd.DataFrame]:
        """Filter and validate today's data."""
        if df is None or df.empty:
            return None
            
        latest_date = df['date'].max()
        df_today = df[df['date'] == latest_date].copy()
        
        min_rows_required = self._get_min_rows_required()
        
        if df_today.empty or len(df_today) < min_rows_required:
            logger.warning(
                f"Insufficient intraday data for {stock_name}: "
                f"have {len(df_today)}, need {min_rows_required}"
            )
            return None
            
        logger.info(f"✅ {stock_name}: {len(df_today)} rows found for today")
        return df_today
    
    def _get_cache_key(self, stock_name: str, data_type: str) -> str:
        """Generate cache key for data."""
        today = datetime.now().date()
        return f"{stock_name}_{data_type}_{today}"
    
    def fetch_intraday_daily_data(self, stock_name: str, security_id: int, 
                                exchange_segment: str, instrument_type: str,
                                use_cache: bool = True) -> Tuple[Optional[pd.DataFrame], 
                                                               Optional[pd.DataFrame], 
                                                               Optional[pd.DataFrame], 
                                                               Optional[datetime]]:
        """
        Enhanced function to fetch 1-minute intraday and daily OHLCV data.

        Args:
            stock_name (str): Trading symbol (e.g. RELIANCE)
            security_id (int): Dhan security ID
            exchange_segment (str): e.g. "NSE_EQ", "BSE_EQ"
            instrument_type (str): e.g. "EQUITY"
            use_cache (bool): Whether to use cached data if available

        Returns:
            tuple: (df_all_intraday, df_today, df_daily, latest_date)
                  Returns (None, None, None, None) if data fetching fails

        Raises:
            DataFetcherError: If input validation fails or critical errors occur
        """
        try:
            # Validate inputs
            self._validate_inputs(stock_name, security_id, exchange_segment, instrument_type)
            
            logger.info(f"Starting data fetch for {stock_name} (ID: {security_id})")
            
            # Check cache for intraday data
            intraday_cache_key = self._get_cache_key(stock_name, "intraday")
            if use_cache and intraday_cache_key in self.cache:
                logger.info(f"Using cached intraday data for {stock_name}")
                df_intraday = self.cache[intraday_cache_key]
            else:
                # Fetch intraday 1-minute OHLCV
                logger.info(f"Fetching intraday data for {stock_name}")
                df_intraday = get_intraday_1min_data(
                    security_id=security_id,
                    exchange_segment=exchange_segment,
                    instrument_type=instrument_type
                )
                
                if df_intraday is None or df_intraday.empty:
                    logger.warning(f"No intraday data received for {stock_name}")
                    return None, None, None, None
                
                # Normalize intraday data
                df_intraday = self._normalize_dataframe(df_intraday, "intraday")
                
                # Cache the data
                if use_cache:
                    self.cache[intraday_cache_key] = df_intraday
            
            # Filter today's data
            df_today = self._filter_today_data(df_intraday, stock_name)
            if df_today is None:
                return None, None, None, None
            
            latest_date = df_today['date'].iloc[-1]
            
            # Check cache for daily data
            daily_cache_key = self._get_cache_key(stock_name, "daily")
            if use_cache and daily_cache_key in self.cache:
                logger.info(f"Using cached daily data for {stock_name}")
                df_daily = self.cache[daily_cache_key]
            else:
                # Fetch daily OHLCV (365 days)
                logger.info(f"Fetching daily data for {stock_name}")
                df_daily = get_daily_ohlcv_data(
                    security_id=security_id,
                    exchange_segment=exchange_segment,
                    instrument_type=instrument_type
                )
                
                if df_daily is None or df_daily.empty:
                    logger.warning(f"No daily OHLCV data for {stock_name}")
                    return df_intraday, df_today, None, latest_date
                
                # Normalize daily data
                df_daily = self._normalize_dataframe(df_daily, "daily")
                
                # Filter to last 365 days
                cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=365)
                df_daily = df_daily[df_daily['timestamp'] >= cutoff_date]
                
                # Cache the data
                if use_cache:
                    self.cache[daily_cache_key] = df_daily
            
            logger.info(f"Successfully fetched data for {stock_name}")
            return df_intraday, df_today, df_daily, latest_date
            
        except DataFetcherError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching data for {stock_name}: {str(e)}")
            raise DataFetcherError(f"Failed to fetch data for {stock_name}: {str(e)}")
    
    def fetch_multiple_stocks(self, stock_list: list, use_metadata: bool = True) -> Dict[str, Any]:
        """
        Fetch data for multiple stocks efficiently.
        
        Args:
            stock_list (list): List of stock symbols or stock metadata dicts
            use_metadata (bool): Whether to use metadata_dict for stock parameters
            
        Returns:
            dict: Dictionary with stock symbols as keys and data tuples as values
        """
        results = {}
        failed_stocks = []
        
        for stock in stock_list:
            try:
                if use_metadata and isinstance(stock, str):
                    if stock not in metadata_dict:
                        logger.warning(f"Stock {stock} not found in metadata_dict")
                        failed_stocks.append(stock)
                        continue
                    
                    metadata = metadata_dict[stock]
                    result = self.fetch_intraday_daily_data(
                        stock_name=stock,
                        security_id=metadata['security_id'],
                        exchange_segment=metadata['exchange_segment'],
                        instrument_type=metadata['instrument_type']
                    )
                elif isinstance(stock, dict):
                    result = self.fetch_intraday_daily_data(**stock)
                else:
                    logger.error(f"Invalid stock format: {stock}")
                    failed_stocks.append(stock)
                    continue
                
                if result[0] is not None:  # If intraday data exists
                    results[stock if isinstance(stock, str) else stock.get('stock_name', 'unknown')] = result
                else:
                    failed_stocks.append(stock)
                    
            except Exception as e:
                logger.error(f"Failed to fetch data for {stock}: {str(e)}")
                failed_stocks.append(stock)
        
        logger.info(f"Successfully fetched data for {len(results)} stocks")
        if failed_stocks:
            logger.warning(f"Failed to fetch data for {len(failed_stocks)} stocks: {failed_stocks}")
        
        return {
            'successful': results,
            'failed': failed_stocks,
            'summary': {
                'total_requested': len(stock_list),
                'successful_count': len(results),
                'failed_count': len(failed_stocks)
            }
        }
    
    def clear_cache(self):
        """Clear the data cache."""
        self.cache.clear()
        logger.info("Data cache cleared")


# Convenience function for backward compatibility
def fetch_intraday_daily_data(stock_name: str, security_id: int, 
                            exchange_segment: str, instrument_type: str):
    """
    Legacy function for backward compatibility.
    """
    fetcher = DhanDataFetcher()
    return fetcher.fetch_intraday_daily_data(stock_name, security_id, exchange_segment, instrument_type)
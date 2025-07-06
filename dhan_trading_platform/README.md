# 🚀 DHAN Trading Platform - Enhanced Data Fetcher

A robust and scalable data fetcher for the DHAN trading platform with enhanced error handling, caching, and professional-grade features.

## 🌟 Features

### ✅ Core Capabilities
- **Intraday & Daily Data**: Fetches 1-minute intraday and daily OHLCV data
- **Multi-Stock Support**: Bulk operations for fetching multiple stocks efficiently
- **Smart Caching**: Intelligent caching system to reduce API calls and improve performance
- **Data Validation**: Comprehensive input validation and data quality checks
- **Time-Aware Logic**: Dynamic minimum row requirements based on trading session time

### 🔧 Technical Enhancements
- **Professional Logging**: Structured logging with file and console outputs
- **Type Safety**: Complete type hints for better IDE support and code documentation
- **Error Handling**: Robust exception handling with custom error classes
- **Object-Oriented Design**: Clean, maintainable, and extensible architecture
- **Backward Compatibility**: Maintains compatibility with existing code

### 📊 Data Quality
- **Normalization**: Consistent timestamp handling and column standardization
- **Null Handling**: Robust processing of missing or invalid data
- **Integrity Checks**: Validation of OHLCV data consistency
- **Market Hours**: Intelligent handling of trading session times

## 📁 Project Structure

```
dhan_trading_platform/
├── core/
│   ├── data_fetcher.py           # Original data fetcher
│   └── data_fetcher_improved.py  # Enhanced version with new features
├── utils/
│   └── dhan_api.py              # DHAN API utility functions
├── config/
│   └── watchlist_metadata.py    # Stock metadata configuration
├── examples/
│   └── data_fetcher_demo.py     # Usage examples and demonstrations
├── requirements.txt             # Project dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### Installation

1. Clone or download the project files
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from core.data_fetcher_improved import DhanDataFetcher

# Initialize the data fetcher
fetcher = DhanDataFetcher()

# Fetch data for a single stock
df_all, df_today, df_daily, latest_date = fetcher.fetch_intraday_daily_data(
    stock_name="RELIANCE",
    security_id=500325,
    exchange_segment="NSE_EQ",
    instrument_type="EQUITY"
)

# Fetch data for multiple stocks using metadata
stock_list = ["RELIANCE", "TCS", "HDFCBANK"]
results = fetcher.fetch_multiple_stocks(stock_list, use_metadata=True)
```

### Using Metadata Configuration

```python
from config.watchlist_metadata import metadata_dict

# Add your stocks to metadata_dict
metadata_dict["NEWSTOCK"] = {
    "security_id": 123456,
    "exchange_segment": "NSE_EQ",
    "instrument_type": "EQUITY",
    "symbol": "NEWSTOCK",
    "company_name": "New Stock Limited"
}
```

## 📋 API Reference

### DhanDataFetcher Class

#### Methods

##### `fetch_intraday_daily_data(stock_name, security_id, exchange_segment, instrument_type, use_cache=True)`

Fetches intraday and daily OHLCV data for a single stock.

**Parameters:**
- `stock_name` (str): Trading symbol (e.g., "RELIANCE")
- `security_id` (int): DHAN security identifier
- `exchange_segment` (str): Exchange segment ("NSE_EQ", "BSE_EQ", etc.)
- `instrument_type` (str): Instrument type ("EQUITY", "FUTURES", etc.)
- `use_cache` (bool): Whether to use cached data (default: True)

**Returns:**
- Tuple: (df_all_intraday, df_today, df_daily, latest_date)

##### `fetch_multiple_stocks(stock_list, use_metadata=True)`

Fetches data for multiple stocks efficiently.

**Parameters:**
- `stock_list` (list): List of stock symbols or metadata dictionaries
- `use_metadata` (bool): Whether to use metadata_dict for parameters

**Returns:**
- Dictionary with successful/failed results and summary statistics

##### `clear_cache()`

Clears the internal data cache.

## 🔍 Examples

### Error Handling

```python
from core.data_fetcher_improved import DhanDataFetcher, DataFetcherError

fetcher = DhanDataFetcher()

try:
    result = fetcher.fetch_intraday_daily_data(
        stock_name="INVALID",
        security_id=-1,  # Invalid ID
        exchange_segment="NSE_EQ",
        instrument_type="EQUITY"
    )
except DataFetcherError as e:
    print(f"Data fetcher error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Cache Performance

```python
import time

fetcher = DhanDataFetcher()

# First call (will cache data)
start = time.time()
result1 = fetcher.fetch_intraday_daily_data("RELIANCE", 500325, "NSE_EQ", "EQUITY")
first_time = time.time() - start

# Second call (uses cache)
start = time.time()
result2 = fetcher.fetch_intraday_daily_data("RELIANCE", 500325, "NSE_EQ", "EQUITY")
second_time = time.time() - start

print(f"Cache speedup: {first_time / second_time:.1f}x faster")
```

### Bulk Operations

```python
# Fetch multiple stocks with custom parameters
stock_configs = [
    {
        "stock_name": "CUSTOM1",
        "security_id": 123456,
        "exchange_segment": "NSE_EQ",
        "instrument_type": "EQUITY"
    },
    {
        "stock_name": "CUSTOM2", 
        "security_id": 654321,
        "exchange_segment": "BSE_EQ",
        "instrument_type": "EQUITY"
    }
]

results = fetcher.fetch_multiple_stocks(stock_configs, use_metadata=False)
print(f"Success rate: {results['summary']['successful_count']}/{results['summary']['total_requested']}")
```

## 📊 Logging

The enhanced data fetcher includes comprehensive logging:

```python
import logging

# Configure custom logging level
logging.getLogger('data_fetcher_improved').setLevel(logging.DEBUG)

# Log files are created automatically as 'dhan_data_fetcher.log'
```

## 🔧 Configuration

### Market Hours Configuration

```python
fetcher = DhanDataFetcher()

# Customize market timing
fetcher.market_open_time = time(9, 15)    # 9:15 AM
fetcher.early_trading_time = time(9, 20)  # 9:20 AM
```

### Valid Exchange Segments
- `NSE_EQ` - NSE Equity
- `BSE_EQ` - BSE Equity  
- `NSE_FO` - NSE Futures & Options
- `NSE_CD` - NSE Currency Derivatives
- `MCX_COM` - MCX Commodities

### Valid Instrument Types
- `EQUITY` - Equity stocks
- `FUTURES` - Futures contracts
- `OPTIONS` - Options contracts
- `COMMODITY` - Commodity contracts

## 🧪 Testing

Run the demo script to test functionality:

```bash
python examples/data_fetcher_demo.py
```

The demo includes:
- Single stock data fetching
- Bulk operations testing
- Cache performance demonstration
- Error handling validation
- Data quality checks

## 🚧 Migration from Original

### Backward Compatibility

The original function is still available:

```python
from core.data_fetcher import fetch_intraday_daily_data

# Original function still works
result = fetch_intraday_daily_data("RELIANCE", 500325, "NSE_EQ", "EQUITY")
```

### Gradual Migration

1. **Phase 1**: Use new class alongside existing code
2. **Phase 2**: Migrate to enhanced error handling and caching
3. **Phase 3**: Adopt bulk operations and advanced features

## 📈 Performance Improvements

| Feature | Original | Enhanced | Improvement |
|---------|----------|----------|-------------|
| Error Handling | Basic | Comprehensive | ✅ Robust |
| Caching | None | Intelligent | 🚀 3-10x faster |
| Bulk Operations | Manual loops | Built-in | ⚡ Efficient |
| Logging | Print statements | Professional | 📊 Observable |
| Type Safety | None | Full coverage | 🛡️ Reliable |

## 🔒 Security Considerations

- **Input Validation**: All parameters are validated before API calls
- **Error Sanitization**: Sensitive information is not logged
- **Rate Limiting**: Built-in support for API rate limiting (optional)
- **Cache Security**: In-memory cache with automatic cleanup

## 🚀 Future Enhancements

- **Async Support**: Non-blocking API calls for better performance
- **Real-time Streaming**: WebSocket support for live data
- **Advanced Caching**: Redis/Memcached integration
- **Monitoring**: Prometheus metrics and health checks
- **Data Pipeline**: ETL capabilities for data warehousing

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed via `requirements.txt`
2. **API Failures**: Check network connectivity and DHAN API credentials
3. **Data Quality**: Review logs for data validation warnings
4. **Performance**: Monitor cache hit rates and adjust accordingly

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show detailed operation logs
```

## 📞 Support

For issues and questions:
1. Check the logs in `dhan_data_fetcher.log`
2. Review the demo script for usage examples
3. Validate your input parameters against the API documentation

## 📄 License

This project is designed for educational and development purposes. Ensure compliance with DHAN API terms of service.

---

🌟 **Star this project if it helps your trading platform development!**
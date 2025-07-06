#!/usr/bin/env python3
"""
Demo script showing usage of the improved DHAN data fetcher.

This script demonstrates:
1. Basic data fetching for a single stock
2. Bulk data fetching for multiple stocks
3. Error handling and logging
4. Cache usage
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_fetcher_improved import DhanDataFetcher, DataFetcherError
from config.watchlist_metadata import metadata_dict
import pandas as pd


def demo_single_stock_fetch():
    """Demonstrate fetching data for a single stock."""
    print("\n" + "="*60)
    print("🔍 DEMO 1: Single Stock Data Fetching")
    print("="*60)
    
    fetcher = DhanDataFetcher()
    
    try:
        # Fetch data for RELIANCE
        stock_name = "RELIANCE"
        if stock_name in metadata_dict:
            metadata = metadata_dict[stock_name]
            
            print(f"📊 Fetching data for {stock_name}...")
            
            df_all, df_today, df_daily, latest_date = fetcher.fetch_intraday_daily_data(
                stock_name=stock_name,
                security_id=metadata['security_id'],
                exchange_segment=metadata['exchange_segment'],
                instrument_type=metadata['instrument_type']
            )
            
            if df_all is not None:
                print(f"✅ Successfully fetched data for {stock_name}")
                print(f"   📈 Intraday records: {len(df_all)}")
                print(f"   📅 Today's records: {len(df_today) if df_today is not None else 0}")
                print(f"   📊 Daily records: {len(df_daily) if df_daily is not None else 0}")
                print(f"   🗓️ Latest date: {latest_date}")
                
                if df_today is not None and not df_today.empty:
                    print(f"\n📋 Today's data sample:")
                    print(df_today[['timestamp', 'open', 'high', 'low', 'close', 'volume']].tail(3))
            else:
                print(f"❌ No data available for {stock_name}")
                
    except DataFetcherError as e:
        print(f"❌ Data fetcher error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def demo_bulk_stock_fetch():
    """Demonstrate fetching data for multiple stocks."""
    print("\n" + "="*60)
    print("🔍 DEMO 2: Bulk Stock Data Fetching")
    print("="*60)
    
    fetcher = DhanDataFetcher()
    
    # List of stocks to fetch
    stock_list = ["RELIANCE", "TCS", "HDFCBANK"]
    
    print(f"📊 Fetching data for {len(stock_list)} stocks: {', '.join(stock_list)}")
    
    try:
        results = fetcher.fetch_multiple_stocks(stock_list, use_metadata=True)
        
        print(f"\n📈 Bulk fetch results:")
        print(f"   ✅ Successful: {results['summary']['successful_count']}")
        print(f"   ❌ Failed: {results['summary']['failed_count']}")
        
        if results['successful']:
            print(f"\n📋 Successfully fetched stocks:")
            for stock_name, (df_all, df_today, df_daily, latest_date) in results['successful'].items():
                today_count = len(df_today) if df_today is not None else 0
                daily_count = len(df_daily) if df_daily is not None else 0
                print(f"   📊 {stock_name}: {today_count} today, {daily_count} daily")
        
        if results['failed']:
            print(f"\n❌ Failed stocks: {', '.join(map(str, results['failed']))}")
            
    except Exception as e:
        print(f"❌ Bulk fetch error: {e}")


def demo_cache_functionality():
    """Demonstrate caching functionality."""
    print("\n" + "="*60)
    print("🔍 DEMO 3: Cache Functionality")
    print("="*60)
    
    fetcher = DhanDataFetcher()
    
    if "RELIANCE" in metadata_dict:
        metadata = metadata_dict["RELIANCE"]
        
        print("📊 First fetch (will cache data)...")
        start_time = pd.Timestamp.now()
        
        try:
            result1 = fetcher.fetch_intraday_daily_data(
                stock_name="RELIANCE",
                security_id=metadata['security_id'],
                exchange_segment=metadata['exchange_segment'],
                instrument_type=metadata['instrument_type'],
                use_cache=True
            )
            
            first_fetch_time = (pd.Timestamp.now() - start_time).total_seconds()
            print(f"⏱️ First fetch time: {first_fetch_time:.2f} seconds")
            
            print("\n📊 Second fetch (will use cache)...")
            start_time = pd.Timestamp.now()
            
            result2 = fetcher.fetch_intraday_daily_data(
                stock_name="RELIANCE",
                security_id=metadata['security_id'],
                exchange_segment=metadata['exchange_segment'],
                instrument_type=metadata['instrument_type'],
                use_cache=True
            )
            
            second_fetch_time = (pd.Timestamp.now() - start_time).total_seconds()
            print(f"⏱️ Second fetch time: {second_fetch_time:.2f} seconds")
            
            if first_fetch_time > 0:
                speedup = first_fetch_time / max(second_fetch_time, 0.001)
                print(f"🚀 Cache speedup: {speedup:.1f}x faster")
            
            # Clear cache
            fetcher.clear_cache()
            print("🧹 Cache cleared")
            
        except Exception as e:
            print(f"❌ Cache demo error: {e}")


def demo_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n" + "="*60)
    print("🔍 DEMO 4: Error Handling")
    print("="*60)
    
    fetcher = DhanDataFetcher()
    
    # Test invalid inputs
    test_cases = [
        {
            "name": "Empty stock name",
            "params": {
                "stock_name": "",
                "security_id": 123456,
                "exchange_segment": "NSE_EQ",
                "instrument_type": "EQUITY"
            }
        },
        {
            "name": "Invalid security ID",
            "params": {
                "stock_name": "TEST",
                "security_id": -1,
                "exchange_segment": "NSE_EQ",
                "instrument_type": "EQUITY"
            }
        },
        {
            "name": "Invalid exchange",
            "params": {
                "stock_name": "TEST",
                "security_id": 123456,
                "exchange_segment": "INVALID_EXCHANGE",
                "instrument_type": "EQUITY"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        try:
            fetcher.fetch_intraday_daily_data(**test_case['params'])
            print("❌ Expected error but got success")
        except DataFetcherError as e:
            print(f"✅ Caught expected error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


def demo_data_quality_checks():
    """Demonstrate data quality validation."""
    print("\n" + "="*60)
    print("🔍 DEMO 5: Data Quality Validation")
    print("="*60)
    
    # Create sample data with quality issues
    import pandas as pd
    from datetime import datetime, timedelta
    
    print("📊 Creating sample data with quality issues...")
    
    # Sample data with various quality issues
    timestamps = [datetime.now() - timedelta(minutes=i) for i in range(10, 0, -1)]
    sample_data = pd.DataFrame({
        'timestamp': timestamps,
        'open': [100, 101, None, 103, 104, 105, 106, 107, 108, 109],  # Missing value
        'high': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
        'low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108],
        'close': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        'volume': [1000, 1500, 2000, 1800, 2200, 1900, 2100, 1700, 1600, 1800]
    })
    
    print(f"📋 Sample data shape: {sample_data.shape}")
    print(f"📉 Missing values in 'open': {sample_data['open'].isna().sum()}")
    
    # Simulate data normalization
    fetcher = DhanDataFetcher()
    normalized_data = fetcher._normalize_dataframe(sample_data, "sample")
    
    print(f"📈 After normalization: {normalized_data.shape}")
    print(f"✅ Data quality check completed")


def main():
    """Run all demo functions."""
    print("🚀 DHAN Data Fetcher - Enhanced Demo")
    print("="*60)
    print("This demo showcases the improved data fetcher capabilities:")
    print("• Enhanced error handling and validation")
    print("• Professional logging and monitoring")
    print("• Intelligent caching system") 
    print("• Bulk operations support")
    print("• Data quality assurance")
    
    try:
        # Run demos (commented out API calls since we don't have real API)
        # demo_single_stock_fetch()
        # demo_bulk_stock_fetch()
        demo_cache_functionality()
        demo_error_handling()
        demo_data_quality_checks()
        
        print("\n" + "="*60)
        print("✅ Demo completed successfully!")
        print("💡 Check the 'dhan_data_fetcher.log' file for detailed logs")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")


if __name__ == "__main__":
    main()
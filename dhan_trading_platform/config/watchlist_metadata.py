"""
Watchlist metadata configuration for DHAN trading platform.
Contains security IDs, exchange segments, and other metadata for stocks.
"""

# Example metadata structure
metadata_dict = {
    "RELIANCE": {
        "security_id": 500325,
        "exchange_segment": "NSE_EQ",
        "instrument_type": "EQUITY",
        "symbol": "RELIANCE",
        "company_name": "Reliance Industries Limited"
    },
    "TCS": {
        "security_id": 532540,
        "exchange_segment": "NSE_EQ", 
        "instrument_type": "EQUITY",
        "symbol": "TCS",
        "company_name": "Tata Consultancy Services Limited"
    },
    "HDFCBANK": {
        "security_id": 500180,
        "exchange_segment": "NSE_EQ",
        "instrument_type": "EQUITY", 
        "symbol": "HDFCBANK",
        "company_name": "HDFC Bank Limited"
    }
    # Add more stocks as needed
}
from SmartApi import SmartConnect
import pandas as pd
from datetime import datetime, timedelta
import credentials
import requests
import numpy as np
from time import time, sleep
import pyotp
import warnings
import os
from talib import EMA, RSI, ATR  # Ensure TA-Lib is installed
from tabulate import tabulate  # Ensure tabulate is installed
from contextlib import redirect_stdout, redirect_stderr

warnings.filterwarnings('ignore')

# Define SYMBOL_LIST (your underlying equities)
SYMBOL_LIST = [
    'AARTIIND', 'ABB', 'ABCAPITAL', 'ABFRL', 'ACC', 'ADANIENSOL', 'ADANIENT',
    'ADANIGREEN', 'ADANIPORTS', 'ALKEM', 'AMBUJACEM', 'ANGELONE', 'APLAPOLLO',
    'APOLLOHOSP', 'APOLLOTYRE', 'ASHOKLEY', 'ASIANPAINT', 'ASTRAL', 'ATGL',
    'AUBANK', 'AUROPHARMA', 'AXISBANK', 'BAJAJ-AUTO', 'BAJAJFINSV', 'BAJFINANCE',
    'BALKRISIND', 'BANDHANBNK', 'BANKBARODA', 'BANKINDIA', 'BEL', 'BERGEPAINT',
    'BHARATFORG', 'BHARTIARTL', 'BHEL', 'BIOCON', 'BOSCHLTD', 'BPCL', 'BRITANNIA',
    'BSE', 'BSOFT', 'CAMS', 'CANBK', 'CDSL', 'CESC', 'CGPOWER', 'CHAMBLFERT',
    'CHOLAFIN', 'CIPLA', 'COALINDIA', 'COFORGE', 'COLPAL', 'CONCOR', 'CROMPTON',
    'CUMMINSIND', 'CYIENT', 'DABUR', 'DALBHARAT', 'DEEPAKNTR', 'DELHIVERY',
    'DIVISLAB', 'DIXON', 'DLF', 'DMART', 'DRREDDY', 'EICHERMOT', 'ESCORTS',
    'EXIDEIND', 'FEDERALBNK', 'GAIL', 'GLENMARK', 'GMRAIRPORT', 'GODREJCP',
    'GODREJPROP', 'GRANULES', 'GRASIM', 'HAL', 'HAVELLS', 'HCLTECH', 'HDFCAMC',
    'HDFCBANK', 'HDFCLIFE', 'HEROMOTOCO', 'HFCL', 'HINDALCO', 'HINDCOPPER',
    'HINDPETRO', 'HINDUNILVR', 'HUDCO', 'ICICIBANK', 'ICICIGI', 'ICICIPRULI',
    'IDEA', 'IDFCFIRSTB', 'IEX', 'IGL', 'IIFL', 'INDHOTEL', 'INDIANB', 'INDIGO',
    'INDUSINDBK', 'INDUSTOWER', 'INFY', 'IOC', 'IRB', 'IRCTC', 'IREDA', 'IRFC',
    'ITC', 'JINDALSTEL', 'JIOFIN', 'JKCEMENT', 'JSL', 'JSWENERGY', 'JSWSTEEL',
    'JUBLFOOD', 'KALYANKJIL', 'KEI', 'KOTAKBANK', 'KPITTECH', 'LAURUSLABS',
    'LICHSGFIN', 'LICI', 'LODHA', 'LT', 'LTF', 'LTIM', 'LTTS', 'LUPIN', 'M&M',
    'M&MFIN', 'MANAPPURAM', 'MARICO', 'MARUTI', 'MAXHEALTH', 'MCX', 'MFSL', 'MGL',
    'MOTHERSON', 'MPHASIS', 'MRF', 'MUTHOOTFIN', 'NATIONALUM', 'NAUKRI', 'NBCC',
    'NCC', 'NESTLEIND', 'NHPC', 'NMDC', 'NTPC', 'NYKAA', 'OBEROIRLTY', 'OFSS',
    'OIL', 'ONGC', 'PAGEIND', 'PATANJALI', 'PAYTM', 'PEL', 'PERSISTENT',
    'PETRONET', 'PFC', 'PHOENIXLTD', 'PIDILITIND', 'PIIND', 'PNB', 'POLICYBZR',
    'POLYCAB', 'POONAWALLA', 'POWERGRID', 'PRESTIGE', 'RAMCOCEM', 'RBLBANK',
    'RECLTD', 'RELIANCE', 'SAIL', 'SBICARD', 'SBILIFE', 'SBIN', 'SHREECEM',
    'SHRIRAMFIN', 'SIEMENS', 'SJVN', 'SOLARINDS', 'SONACOMS', 'SRF', 'SUNPHARMA',
    'SUPREMEIND', 'SYNGENE', 'TATACHEM', 'TATACOMM', 'TATACONSUM', 'TATAELXSI',
    'TATAMOTORS', 'TATAPOWER', 'TATASTEEL', 'TATATECH', 'TCS', 'TECHM', 'TIINDIA',
    'TITAGARH', 'TITAN', 'TORNTPHARM', 'TORNTPOWER', 'TRENT', 'TVSMOTOR',
    'ULTRACEMCO', 'UNIONBANK', 'UNITDSPR', 'UPL', 'VBL', 'VEDL', 'VOLTAS',
    'WIPRO', 'YESBANK', 'ZOMATO', 'ZYDUSLIFE'
]
TRADED_SYMBOL = []
timeFrame = 10  # Interval for historical API calls

#-------------------------------------------------------------------
def intializeSymbolTokenMap():
    url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
    d = requests.get(url).json()
    global token_df
    token_df = pd.DataFrame.from_dict(d)
    token_df['expiry'] = pd.to_datetime(token_df['expiry'])
    token_df = token_df.astype({'strike': float})
    credentials.TOKEN_MAP = token_df

#-------------------------------------------------------------------
def getTokenInfo(symbol, exch_seg='NSE', instrumenttype='OPTIDX', strike_price='', pe_ce='CE'):
    df = credentials.TOKEN_MAP
    strike_price = strike_price * 100
    if exch_seg == 'NSE':
        eq_df = df[(df['exch_seg'] == 'NSE') & (df['symbol'].str.contains('EQ'))]
        return eq_df[eq_df['name'] == symbol]
    elif exch_seg == 'NFO' and instrumenttype in ['FUTSTK', 'FUTIDX']:
        return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) &
                  (df['name'] == symbol)].sort_values(by=['expiry'])
    elif exch_seg == 'NFO' and instrumenttype in ['OPTSTK', 'OPTIDX']:
        return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) &
                  (df['name'] == symbol) & (df['symbol'].str.endswith(pe_ce))].sort_values(by=['expiry'])

#-------------------------------------------------------------------
def calculate_inidcator(res_json):
    """
    Calculate technical indicators (EMA, RSI, ATR) from candle data and print the latest 10 rows.
    """
    if not res_json or 'data' not in res_json:
        print("❌ No data received from API!")
        return None
    columns = ['timestamp', 'O', 'H', 'L', 'C', 'V']
    df = pd.DataFrame(res_json['data'], columns=columns)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%dT%H:%M:%S')
    for col in ['O', 'H', 'L', 'C', 'V']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['EMA'] = EMA(df['C'].to_numpy(), timeperiod=20)
    df['RSI'] = RSI(df['C'].to_numpy(), timeperiod=14)
    df['ATR'] = ATR(df['H'].to_numpy(), df['L'].to_numpy(), df['C'].to_numpy(), timeperiod=20)
    latest_rows = df[['timestamp', 'C', 'EMA', 'RSI', 'ATR']].tail(10)
    table = tabulate(latest_rows, headers='keys', tablefmt='fancy_grid')
    print("\n📊 Latest Trading Data with Indicators")
    print(table)
    return df

#-------------------------------------------------------------------
def getHistoricalAPI(token, interval='ONE_MINUTE'):
    to_date = datetime.now()
    from_date = to_date - timedelta(days=2)
    from_date_format = from_date.strftime("%Y-%m-%d %H:%M")
    to_date_format = to_date.strftime("%Y-%m-%d %H:%M")
    print(from_date_format, to_date_format)
    try:
        historicParam = {
            "exchange": "NSE",
            "symboltoken": token,
            "interval": interval,
            "fromdate": from_date_format,
            "todate": to_date_format
        }
        candle_json = credentials.SMART_API_OBJ.getCandleData(historicParam)
        return calculate_inidcator(candle_json)
    except Exception as e:
        print("Historic API failed:", e)

#-------------------------------------------------------------------
def place_order(token, symbol, qty, buy_sell, ordertype, price, producttype='DELIVERY',
                variety='NORMAL', exch_seg='NSE', triggerprice=0):
    try:
        orderparams = {
            "variety": variety,
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": buy_sell,
            "exchange": exch_seg,
            "ordertype": ordertype,
            "producttype": producttype,
            "duration": "DAY",
            "price": price,
            "squareoff": "0",
            "stoploss": "0",
            "quantity": qty,
            "triggerprice": triggerprice
        }
        orderId = credentials.SMART_API_OBJ.placeOrder(orderparams)
        print("Order id:", orderId)
        return orderId
    except Exception as e:
        print("Order placement failed:", e)

#-------------------------------------------------------------------
def get_previous_trading_day_candle(token, exchange="NSE"):
    """
    Fetch the previous trading day's candle for the given token using the ONE_DAY interval.
    Determines the last trading day based on the current weekday:
      - If today is Monday, previous trading day is Friday (3 days ago).
      - If today is Saturday or Sunday, previous trading day is Friday.
      - Otherwise, it is yesterday.
    
    Returns a dictionary with keys:
      'prev_open', 'prev_high', 'prev_low', 'prev_close'
    If data is unavailable, returns zeros.
    """
    now = datetime.now()
    weekday = now.weekday()  # Monday=0, Tuesday=1, ..., Sunday=6

    if weekday == 0:  # Monday → use Friday (3 days ago)
        last_trading_day = now - timedelta(days=3)
    elif weekday in [5, 6]:  # Saturday or Sunday → use Friday
        last_trading_day = now - timedelta(days=(weekday - 4))
    else:
        last_trading_day = now - timedelta(days=1)
    
    date_str = last_trading_day.strftime("%Y-%m-%d")
    from_date_format = f"{date_str} 00:00"
    to_date_format = f"{date_str} 23:59"
    print(f"[DEBUG] Fetching historical daily candle data from {from_date_format} to {to_date_format} for token {token}")
    
    try:
        params = {
            "exchange": exchange,
            "symboltoken": token,
            "interval": "ONE_DAY",
            "fromdate": from_date_format,
            "todate": to_date_format
        }
        candle_json = credentials.SMART_API_OBJ.getCandleData(params)
        print(f"[DEBUG] Raw historical candle data for token {token}: {candle_json}")
        if candle_json.get("status") and candle_json.get("data"):
            # Assume the last candle is for the last trading day
            last_candle = candle_json["data"][-1]
            prev_data = {
                "prev_open": last_candle[1],
                "prev_high": last_candle[2],
                "prev_low": last_candle[3],
                "prev_close": last_candle[4]
            }
            print(f"[DEBUG] Previous trading day candle for token {token} found: {prev_data}")
            return prev_data
        else:
            print(f"[DEBUG] No historical data returned for token {token}. Returning zeros.")
            return {"prev_open": 0, "prev_high": 0, "prev_low": 0, "prev_close": 0}
    except Exception as e:
        print(f"Error fetching previous day candle for token {token}: {e}")
        return {"prev_open": 0, "prev_high": 0, "prev_low": 0, "prev_close": 0}


#-------------------------------------------------------------------
def compute_call_score(row):
    tol = 0.01
    scores = {}
    scores['open_equals_low'] = 1 if abs(row['open'] - row['low']) < tol else 0
    scores['netChange_positive'] = 1 if row['netChange'] > 0 else 0
    # Removed: scores['close_gt_open']     scores['close_gt_open'] = 1 if row['close'] > row['open'] else 0
    scores['lower_range_gt_upper_range'] = 1 if (row['open'] - row['low']) > (row['high'] - row['close']) else 0
    scores['close_ge_prev_open'] = 1 if row['close'] >= row['prev_open'] else 0
    scores['open_le_prev_close'] = 1 if row['open'] <= row['prev_close'] else 0
    scores['high_gt_prev_high'] = 1 if row['high'] > row['prev_high'] else 0
    scores['low_lt_prev_low'] = 1 if row['low'] < row['prev_low'] else 0
    scores['close_gt_prev_close'] = 1 if row['close'] > row['prev_close'] else 0
    scores['total'] = sum(scores.values())
    return scores

def compute_put_score(row):
    tol = 0.01
    scores = {}
    scores['open_equals_high'] = 1 if abs(row['open'] - row['high']) < tol else 0
    scores['netChange_negative'] = 1 if row['netChange'] < 0 else 0
    # Removed: scores['close_lt_open']     scores['close_lt_open'] = 1 if row['close'] < row['open'] else 0
    scores['upper_range_gt_lower_range'] = 1 if (row['high'] - row['open']) > (row['close'] - row['low']) else 0
    scores['close_le_prev_open'] = 1 if row['close'] <= row['prev_open'] else 0
    scores['open_ge_prev_close'] = 1 if row['open'] >= row['prev_close'] else 0
    scores['high_lt_prev_high'] = 1 if row['high'] < row['prev_high'] else 0
    scores['low_gt_prev_low'] = 1 if row['low'] > row['prev_low'] else 0
    scores['close_lt_prev_close'] = 1 if row['close'] < row['prev_close'] else 0
    scores['total'] = sum(scores.values())
    return scores

#-------------------------------------------------------------------
def filter_sustainable_equities(data):
    """
    Flatten market data, compute scores for each candidate, and select top candidates.
    
    For Call options, we filter for equities where:
      - open equals low (within tolerance), and 
      - netChange is positive.
    
    For Put options, we filter for equities where:
      - open equals high (within tolerance), and 
      - netChange is negative.
    
    Then, for each candidate, we compute a score based on additional conditions.
    The top three candidates (by total score) for calls and puts are returned.
    """
    if not data:
        print("⚠️ No market data received. Skipping filtering.")
        return [], []
    
    # Flatten the list of lists
    flat_data = [equity for sublist in data for equity in sublist]
    df = pd.DataFrame(flat_data)
    
    print("\n📝 Columns in Market Data:", df.columns.tolist())
    if set(['tradingSymbol', 'open', 'low', 'high', 'close', 'ltp', 'tradeVolume']).issubset(df.columns):
        print("\n📝 First 10 rows of selected columns:")
        print(tabulate(df[['tradingSymbol', 'open', 'low', 'high', 'close', 'ltp', 'tradeVolume']].head(10),
                       headers='keys', tablefmt='fancy_grid'))
    
    expected_cols = ['tradingSymbol', 'ltp', 'open', 'high', 'low', 'close',
                     'tradeVolume', 'opnInterest', 'totBuyQuan', 'totSellQuan', 'netChange']
    missing = [col for col in expected_cols if col not in df.columns]
    if missing:
        print("Missing columns in data:", missing)
        return [], []
    
    for col in expected_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=expected_cols, inplace=True)
    
    # For previous day data, if columns are missing then fill with NaN and then attempt to fetch
    prev_cols = ['prev_open', 'prev_close', 'prev_high', 'prev_low']
    for col in prev_cols:
        if col not in df.columns:
            df[col] = np.nan
    # Instead of dropping rows, fill missing previous day data with 0 if fetching fails
    missing_prev = [col for col in prev_cols if df[col].isna().all()]
    if missing_prev:
        print("Missing previous day columns in data:", missing_prev)
        print("Fetching previous day data for each equity...")
        for idx, row in df.iterrows():
            token = row['symbolToken']
            exchange = row.get('exchange', "NSE")
            prev_data = get_previous_trading_day_candle(token, exchange=exchange)
            if prev_data:
                df.at[idx, 'prev_open'] = prev_data.get('prev_open', 0)
                df.at[idx, 'prev_close'] = prev_data.get('prev_close', 0)
                df.at[idx, 'prev_high'] = prev_data.get('prev_high', 0)
                df.at[idx, 'prev_low'] = prev_data.get('prev_low', 0)
            else:
                df.at[idx, 'prev_open'] = 0
                df.at[idx, 'prev_close'] = 0
                df.at[idx, 'prev_high'] = 0
                df.at[idx, 'prev_low'] = 0
    df[prev_cols] = df[prev_cols].fillna(0)
    
    # Basic filtering conditions:
    # For calls: open equals low (within tolerance) and netChange is positive.
    call_df = df[(abs(df['open'] - df['low']) < 0.001) &
                 (df['netChange'] > 0)].copy()
    # For puts: open equals high (within tolerance) and netChange is negative.
    put_df = df[(abs(df['open'] - df['high']) < 0.001) &
                (df['netChange'] < 0)].copy()
    
    # Compute and assign total score for each candidate.
    if not call_df.empty:
        call_df['total'] = call_df.apply(lambda row: compute_call_score(row)['total'], axis=1)
        call_df_sorted = call_df.sort_values(by='total', ascending=False)
    else:
        call_df_sorted = call_df

    if not put_df.empty:
        put_df['total'] = put_df.apply(lambda row: compute_put_score(row)['total'], axis=1)
        put_df_sorted = put_df.sort_values(by='total', ascending=False)
    else:
        put_df_sorted = put_df
        
    # Display complete score tables.
    print("\n📊 Score Table for Call Candidates:")
    call_display_cols = ['tradingSymbol', 'open', 'low', 'close', 'netChange', 'prev_open', 'prev_close', 'total']
    if not call_df_sorted.empty:
        print(tabulate(call_df_sorted[call_display_cols].head(10), headers="keys", tablefmt="fancy_grid", showindex=False))
    else:
        print("No call candidates to score.")
    
    print("\n📊 Score Table for Put Candidates:")
    put_display_cols = ['tradingSymbol', 'open', 'high', 'close', 'netChange', 'prev_open', 'prev_close', 'total']
    if not put_df_sorted.empty:
        print(tabulate(put_df_sorted[put_display_cols].head(10), headers="keys", tablefmt="fancy_grid", showindex=False))
    else:
        print("No put candidates to score.")
    
    # Select the top three candidates from each side.
    top_call_candidates = call_df_sorted.head(3).to_dict('records')
    top_put_candidates = put_df_sorted.head(3).to_dict('records')
    
    # For consistency, return these as filteredCallData and filteredPutData.
    filteredCallData = top_call_candidates
    filteredPutData = top_put_candidates
    return filteredCallData, filteredPutData

#-------------------------------------------------------------------
def save_execution_data(result_df):
    """
    Save the result DataFrame as a CSV file and backup the Python script.
    """
    output_folder = "/Users/prakashmansara/Desktop/ExecutionData"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created directory: {output_folder}")
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    csv_file_path = f"{output_folder}/mainmodified270325_{timestamp}.csv"
    script_file_path = f"{output_folder}/mainmodified270325_{timestamp}.txt"
    try:
        result_df.to_csv(csv_file_path, index=False)
        print(f"📂 CSV saved successfully at: {csv_file_path}")
    except Exception as e:
        print("❌ Error saving CSV:", e)
    script_path = "/Users/prakashmansara/LOH/main modified 27.03.2025.py"
    try:
        with open(script_path, "r") as script_file:
            script_content = script_file.read()
        with open(script_file_path, "w") as output_script_file:
            output_script_file.write(script_content)
        print(f"📜 Python script backup saved at: {script_file_path}")
    except Exception as e:
        print("❌ Error saving script backup:", e)
    print('------------------------------------------------------------------------------------------------------------------------------------------------------------')

#-------------------------------------------------------------------
def checkSingnal():
    startTime = time()
    global TRADED_SYMBOL
    token_list = []
    # Get token info for each symbol
    for symbol in SYMBOL_LIST:
        if symbol not in TRADED_SYMBOL:
            tokenInfo = getTokenInfo(symbol)
            if tokenInfo.empty:
                print("Error getting token info for:", symbol)
                continue
            tokenInfo = tokenInfo.iloc[0]
            token_list.append(tokenInfo['token'])
    print("------------------------------------------------------------------------")
    print(f"✅ Total equity tokens analyzed: {len(token_list)}")
    
    # Batch tokens in groups of 45
    tokenFinalList = []
    tempTokenList = []
    for t in token_list:
        tempTokenList.append(t)
        if len(tempTokenList) == 45:
            tokenFinalList.append(tempTokenList)
            tempTokenList = []
    if tempTokenList:
        tokenFinalList.append(tempTokenList)
    
    data = []
    for tokens in tokenFinalList:
        exchangeToken = {"NSE": tokens}
        marketData = obj.getMarketData("FULL", exchangeToken)
        dataTemp = marketData['data']['fetched']
        data.append(dataTemp)
        sleep(0.5)
    
    total_records = sum(len(d) for d in data if isinstance(d, list))
    print(f"✅ Total records fetched: {total_records}")
    
    # Filter equities (calls and puts) using our function
    filteredCallData, filteredPutData = filter_sustainable_equities(data)
    
    # Define the columns to display in the score tables
    selected_columns = [
        'tradingSymbol', 'ltp', 'open', 'high', 'low', 'close',
        'netChange', 'tradeVolume', 'opnInterest'
    ]
    
    print("\n📊 Final Shortlisted Call Equities:")
    if filteredCallData:
        call_df = pd.DataFrame(filteredCallData)
        call_cols = [col for col in selected_columns if col in call_df.columns]
        print(tabulate(call_df[call_cols], headers="keys", tablefmt="fancy_grid", showindex=False))
    else:
        print("⚠️ No Call equities met the criteria.")
    
    print("\n📊 Final Shortlisted Put Equities:")
    if filteredPutData:
        put_df = pd.DataFrame(filteredPutData)
        put_cols = [col for col in selected_columns if col in put_df.columns]
        print(tabulate(put_df[put_cols], headers="keys", tablefmt="fancy_grid", showindex=False))
    else:
        print("⚠️ No Put equities met the criteria.")
    
    if not (filteredCallData or filteredPutData):
        print("⚠️ No stocks met the criteria for Call or Put. Exiting.")
        print(f"Total time taken: {time() - startTime:.2f} seconds")
        return
    
    # Mark option type for each equity
    for equity in filteredCallData:
        equity['optionType'] = 'CE'
    for equity in filteredPutData:
        equity['optionType'] = 'PE'
    
    finalSortedData = filteredCallData + filteredPutData
    
    # Retrieve current available balance
    currentAvailableBalance = obj.rmsLimit()
    if currentAvailableBalance:
        currentAvailableBalance = float(currentAvailableBalance['data']['availablecash'])
        print(f"CURRENT BALANCE IN MY ANGLE ACCOUNT IS: {currentAvailableBalance}")
    else:
        print("Error retrieving available balance")
    
    # Initialize order execution summary DataFrame
    result_df = pd.DataFrame(columns=['token', 'ATMsymbol', 'equity', 'ltp', 'lotsize', 'buyPrice', 'openInterest'])
    result_df_ind = 0
    insufficient_funds_list = []
    
    # Loop through shortlisted equities and attempt to place BUY orders
    for equity in finalSortedData:
        tokenInfo = getTokenInfo(equity['tradingSymbol'].split('-')[0],
                                  exch_seg='NFO', instrumenttype='OPTSTK', pe_ce=equity['optionType'])
        tokenInfo = tokenInfo[tokenInfo['symbol'].str.contains('27MAR25')]
        if tokenInfo.empty:
            print(f"⚠️ No valid option found for {equity['tradingSymbol']}")
            continue
        nearest_index = (tokenInfo['strike'] - equity['open'] * 100).abs().idxmin()
        nearest_token = tokenInfo.loc[nearest_index]
        try:
            currentLtpData = obj.getMarketData('FULL', {'NFO': [nearest_token['token']]})
            currentPrice = currentLtpData['data']['fetched'][0]['ltp']
            openInterest = currentLtpData['data']['fetched'][0]['opnInterest']
            buyPrice = currentPrice * float(nearest_token['lotsize'])
            result_df.loc[result_df_ind] = [nearest_token['token'], nearest_token['symbol'],
                                             nearest_token['name'], currentPrice,
                                             nearest_token['lotsize'], buyPrice, openInterest]
            result_df_ind += 1
            if currentAvailableBalance < buyPrice:
                insufficient_funds_list.append([nearest_token['symbol'], buyPrice,
                                                  currentAvailableBalance, buyPrice - currentAvailableBalance])
                print(f"⚠️ Skipping {nearest_token['symbol']} due to insufficient funds")
            else:
                print(f"Placing order to BUY {nearest_token['symbol']} at LTP {currentPrice} "
                      f"with lotsize {nearest_token['lotsize']} and total buyPrice {buyPrice}")
                orderRes = place_order(nearest_token['token'], nearest_token['symbol'],
                                        int(nearest_token['lotsize']), 'BUY', 'MARKET', 0,
                                        'CARRYFORWARD', 'NORMAL', 'NFO')
                print("Order placed:", orderRes)
        except Exception as e:
            print("--------error while getting live market data-------")
            print(e)
        sleep(0.7)
    
    if insufficient_funds_list:
        headers = ["ATMsymbol", "Required Buy Price", "Available Balance", "Shortfall"]
        funds_table = tabulate(insufficient_funds_list, headers=headers, tablefmt="fancy_grid")
        print("\n💰 INSUFFICIENT FUNDS - EQUITIES NOT BOUGHT")
        print(funds_table)
    else:
        print("\n✅ Sufficient funds available for all selected equities!")
    
    print('----------------------------------------------INVESTMENT SUMMARY----------------------------------------------')
    if not result_df.empty:
        ordered_cols = ['ATMsymbol', 'ltp', 'lotsize', 'buyPrice', 'openInterest', 'equity']
        summary_table = tabulate(result_df[ordered_cols], headers="keys", tablefmt="fancy_grid", showindex=False)
        print("📊 BUY PRICE SUMMARY:")
        print(summary_table)
    else:
        print("No orders generated.")
        
    print('----------------------------------------------INVESTMENT REQUIRE TO BUY OPTIN EQUITY TODAY:-----------------------------------------------------------------')
    print(f"📊 BUY PRICE SUMMARY:\n"
          f"✅ MAX: {result_df['buyPrice'].max()} | "
          f"✅ MIN: {result_df['buyPrice'].min()} | "
          f"✅ TOTAL: {result_df['buyPrice'].sum()}")
    print('------------------------------------------------------------------------------------------------------------------------------------------------------------')
    
    print('------------------------------------------------------------------------------------------------------------------------------------------------------------')
    save_execution_data(result_df)
    print(f"Total time taken: {time() - startTime:.2f} seconds")

#-------------------------------------------------------------------
def trailingStopLoss(tokenInfo, buyPrice, stopLossPercentage):
    exchangeToken = {tokenInfo['exch_seg']: [tokenInfo['token']]}
    buyPrice = float(buyPrice)
    highPrice = buyPrice
    sellPrice = highPrice - ((highPrice * stopLossPercentage) / 100)
    print(f"initial sell price = {sellPrice}")
    while True:
        currentData = obj.getMarketData('LTP', exchangeToken)
        if currentData['status']:
            if currentData['data']['fetched']:
                ltp = currentData['data']['fetched'][0]['ltp']
                print(f"ltp of {tokenInfo['symbol']} at {datetime.now()} is {ltp} and current sell price is {sellPrice}")
                if ltp >= highPrice:
                    highPrice = ltp
                    sellPrice = highPrice - ((highPrice * stopLossPercentage) / 100)
                if ltp <= sellPrice:
                    print(f"Sell at {ltp}")
                    sellRes = place_order(tokenInfo['token'], tokenInfo['symbol'],
                                            int(tokenInfo['lotsize']), 'SELL', 'MARKET', 0,
                                            'CARRYFORWARD', 'NORMAL', 'NFO')
                    print("Sell order response:", sellRes)
                    break
        else:
            print('Error while fetching data from SmartAPI')
        sleep(2)

#-------------------------------------------------------------------
if __name__ == '__main__':
    # Save terminal output to a text file if executed successfully.
    output_filename = f"/Users/prakashmansara/Desktop/ExecutionData/terminal270325_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    
    ##-------------------------------------------------------------------
    #If you want to see output in the terminal, comment out or remove the redirection lines:

    #with open(output_filename, "w") as outfile:
    #    with redirect_stdout(outfile), redirect_stderr(outfile):
   
       #-------------------------------------------------------------------

   #if wants above code to run in terminal, press tabe to subindent below codes
   
    intializeSymbolTokenMap()
    obj = SmartConnect(api_key=credentials.API_KEY)
    session_data = obj.generateSession(credentials.USER_NAME, credentials.PWD,
                                        pyotp.TOTP(credentials.TOTP_token).now())
    credentials.SMART_API_OBJ = obj
    sleep(1)
    entryTime = datetime.now()
    print(f"Code start Running at {entryTime}")
    checkSingnal()
    exitTime = datetime.now()
    print(f"Total time taken is {exitTime - entryTime}")
    print("Code execution completed at:", exitTime)
    print(f"Terminal output has been saved to: {output_filename}")
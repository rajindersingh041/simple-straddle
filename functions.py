from datetime import datetime
from alice_blue import *
from time import sleep
from utils import *

banknifty_symbol = 'Nifty Bank'
now = datetime.now()
STRADDLE_START_TIME = now.replace(hour=9, minute=0, second=0, microsecond=0).time()
NORMAL_STRADDLE_SELL_TIME = now.replace(hour=9, minute=30, second=0, microsecond=0).time()
NORMAL_STRADDLE_EXIT_TIME = now.replace(hour=15, minute=18, second=0, microsecond=0).time()

global stocks
stocks = {}

def normal_straddle_logic(alice, option_symbol):
    if option_symbol is None:
        return
    
    if stocks[option_symbol]['normal_stradle_exit'] == True or 'ltp' not in stocks[option_symbol]:
        return
    
    now = get_current_ist()
    curr_time = str(now)[11:]

    if now.time() > NORMAL_STRADDLE_SELL_TIME and stocks[option_symbol]['normal_stradle_price'] == 0:
        stocks[option_symbol]['normal_stradle_price'] = stocks[option_symbol]['ltp']
        print(f"NORMAL_STRADLE: SELL {option_symbol} on {curr_time} at {stocks[option_symbol]['ltp']}")
        place_order(alice, option_symbol, 'sell')
    elif stocks[option_symbol]['normal_stradle_exit'] == False and stocks[option_symbol]['normal_stradle_price'] != 0 and stocks[option_symbol]['ltp'] >= 1.25*stocks[option_symbol]['normal_stradle_price']:
        print(f"NORMAL_STRADLE: BUY (stoploss) {option_symbol} on {curr_time} at {stocks[option_symbol]['ltp']}, stoploss ratio: {round(stocks[option_symbol]['ltp']/stocks[option_symbol]['normal_stradle_price'], 2)}")
        place_order(alice, option_symbol, 'buy')
        stocks[option_symbol]['normal_stradle_exit'] = True
    elif stocks[option_symbol]['normal_stradle_exit'] == False and now.time() >= NORMAL_STRADDLE_EXIT_TIME:
        print(f"NORMAL_STRADLE: BUY {option_symbol} on {curr_time} at {stocks[option_symbol]['ltp']}")
        place_order(alice, option_symbol, 'buy')
        stocks[option_symbol]['normal_stradle_exit'] = True

def order(alice, ce_symbol, pe_symbol):
    while True:
        if stocks[banknifty_symbol]['nearest_hundred'] != 0:
            # NORMAL STRADDLE
            normal_straddle_logic(alice, ce_symbol)
            normal_straddle_logic(alice, pe_symbol)

def StartConnection(alice):
    socket_opened = False
    def event_handler_quote_update(message):
        symbol = message['instrument'].symbol
        ltp = float(message['ltp'])
        if symbol == 'Nifty Bank' and symbol not in stocks:
            stocks[symbol] = {}
            stocks[symbol]['nearest_hundred'] = 0
        stocks[symbol]['ltp'] = ltp

    def open_callback():
        global socket_opened
        socket_opened = True

    alice.start_websocket(subscribe_callback=event_handler_quote_update,
                        socket_open_callback=open_callback,
                        run_in_background=True)
    alice.subscribe(alice.get_instrument_by_symbol('NSE', banknifty_symbol), LiveFeedType.MARKET_DATA)
    sleep(5)
    
    while True:
        now = get_current_ist()
        if now.time() > STRADDLE_START_TIME and stocks[banknifty_symbol]['nearest_hundred'] == 0:
            nearest_hundred = round(stocks[banknifty_symbol]['ltp']/100)
            nearest_hundred = nearest_hundred*100

            stocks[banknifty_symbol]['nearest_hundred'] = nearest_hundred

            expiry = find_expiry()
            ce_symbol = f"BANKNIFTY {expiry} {nearest_hundred}.0 CE"
            pe_symbol = f"BANKNIFTY {expiry} {nearest_hundred}.0 PE"

            ce_instrument = alice.get_instrument_by_symbol('NFO', ce_symbol)
            pe_instrument = alice.get_instrument_by_symbol('NFO', pe_symbol)

            ce_tk = ce_instrument[1]
            pe_tk = pe_instrument[1]

            print(f"CE: {ce_symbol} | {ce_tk}")
            print(f"PE: {pe_symbol} | {pe_tk}")

            stocks[ce_symbol] = {
                'token': ce_tk,
                'normal_stradle_price': 0,
                'normal_stradle_exit': False
            }
            stocks[pe_symbol] = {
                'token': pe_tk,
                'normal_stradle_price': 0,
                'normal_stradle_exit': False
            }

            alice.subscribe([ce_instrument, pe_instrument], LiveFeedType.MARKET_DATA)
            order(alice, ce_symbol, pe_symbol)
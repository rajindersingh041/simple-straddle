from datetime import datetime, timedelta, date
from pytz import timezone
from alice_blue import *

def get_current_ist():
    india = timezone('Asia/Kolkata')
    ist = datetime.now(india)
    return ist

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + timedelta(days_ahead)

def find_expiry():
    months = {1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR', 5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}
    central = str(get_current_ist())[:10]
    date_parts = central.split('-')
    month = int(date_parts[1])
    year = int(date_parts[0])
    day = int(date_parts[2])

    d = date(year, month, day)
    next_thurs = str(next_weekday(d, 3)).split('-')
    next_thursday = int(next_thurs[2])
    if next_thursday - 7 == day:
        next_thursday = day
    
    if next_thursday >= 1 and next_thursday <= 9:
        next_thursday = f"0{next_thursday}"
    
    d = date(int(next_thurs[0]), int(next_thurs[1]), int(next_thurs[2]))
    next_to_next_thurs = str(next_weekday(d, 3)).split('-')
    if next_to_next_thurs[1] != int(central.split('-')[1]):
        return months[int(next_thurs[1])]
    else:
        return f"{next_thursday} {months[int(next_thurs[1])]}"

def place_order(alice, symbol, txn):
    try:
        if txn.lower() == "buy":
            txn_type = TransactionType.Buy
        elif txn.lower() == "sell":
            txn_type = TransactionType.Sell
        
        alice.place_order(
            transaction_type = txn_type,
            instrument = alice.get_instrument_by_symbol('NFO', symbol),
            quantity = 1,
            order_type = OrderType.Market,
            product_type = ProductType.Intraday,
            price = 0.0,
            trigger_price = None,
            stop_loss = None,
            square_off = None,
            trailing_sl = None,
            is_amo = False
        )
    except Exception as e:
        print("Order placement failed")
"""
A simple script that tries to buy an amount of USDC with ARS in small chunks

config.json requires the value api_key like
{"api_key": "...."}

Example buy 1000 USDC pay max 180 pesos per USD doing 100 USDC chunks:
python buy_usdc.py config.json 1000 180 100

"""
import requests
import sys
import time 
import json
import ccxt

PAIR = "USDC_ARS"
NORMAL_WAIT = 10
WAIT_BETWEEN_TRADES = 30
MIN_ORDER = 10

def run(amount_to_buy, limit, chunk, config):
    ripio = ccxt.ripio({'apiKey': config['api_key']})
    # markets = ripio.load_markets()

    total_bought = 0
    while total_bought < amount_to_buy:

        orderbook = ripio.fetch_order_book(PAIR)
        if len(orderbook['asks']) == 0:
            time.sleep(NORMAL_WAIT)
            continue

        top_price, top_amount = orderbook['asks'][0]
        print("current top %s @ %s" % (top_amount, top_price))
        if top_price > limit:
            #too expensive
            time.sleep(NORMAL_WAIT)
            continue

        chunk_to_buy = min(top_amount, chunk)
        chunk_to_buy = max(chunk_to_buy, MIN_ORDER)

        order = ripio.create_limit_buy_order('USDC/ARS', chunk_to_buy, top_price)
        order_id = order['id']
        time.sleep(1)
        # order_id = '8566f8fe-1aba-49c5-8a90-80acff8a5acb'

        order = ripio.fetch_order(order_id, 'USDC/ARS')
        print(order['status'])
        if order['status'] == "closed":
            completed = order['amount']
            total_bought += completed
            print("Completed %s @ %s" % (order['amount'], top_price))
            print("Total %s" % total_bought)
            print()
            time.sleep(WAIT_BETWEEN_TRADES)

    print("WOOHOO DONE COMPRE: %s USDC" % total_bought)

if __name__ == "__main__":
    config = json.load(open(sys.argv[1], "r"))
    amount = float(sys.argv[2])
    limit = float(sys.argv[3])
    chunk = float(sys.argv[4])

    print("""CONFIRM:
Buying: %s USDC
Limit price: %s ARS
Chunk size: %s USDC
""" % (amount, limit, chunk))
    if input("confirm y/n: ") == "y":
        print()
        run(amount, limit, chunk, config)

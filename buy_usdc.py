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

from utils import retry

PAIR = "USDC_ARS"
NORMAL_WAIT = 10
WAIT_BETWEEN_TRADES = 30
MIN_ORDER = 10

@retry(times=5, exceptions=(ccxt.errors.RequestTimeout))
def fetch_order_book(exchange, pair):
    return exchange.fetch_order_book(pair)

@retry(times=5, exceptions=(ccxt.errors.RequestTimeout))
def create_limit_buy_order(exchange, pair, chunk_to_buy, price_to_buy):
    return exchange.create_limit_buy_order(pair, chunk_to_buy, price_to_buy)

@retry(times=5, exceptions=(ccxt.errors.RequestTimeout))
def fetch_order(exchange, order_id, pair):
    return exchange.fetch_order(order_id, pair)

def run(amount_to_buy, limit, chunk, config):
    ripio = ccxt.ripio({'apiKey': config['api_key']})
    # markets = ripio.load_markets()

    total_bought = 0
    while total_bought < amount_to_buy:

        orderbook = fetch_order_book(ripio, PAIR)
        if len(orderbook['asks']) == 0:
            time.sleep(NORMAL_WAIT)
            continue

        top_price, top_amount = orderbook['asks'][0]
        print("current top %s @ %s" % (top_amount, top_price))
        if top_price < limit:
            chunk_to_buy = min(top_amount, chunk)
            chunk_to_buy = max(chunk_to_buy, MIN_ORDER)
            price_to_buy = top_price
        else:
            chunk_to_buy = chunk
            price_to_buy = limit

        order = create_limit_buy_order(ripio, 'USDC/ARS', chunk_to_buy, price_to_buy)
        order_id = order['id']
        # order_id = '8566f8fe-1aba-49c5-8a90-80acff8a5acb'

        while True:
            order = fetch_order(ripio, order_id, 'USDC/ARS')
            if order['status'] != "closed":
                try:
                    orderbook = fetch_order_book(ripio, PAIR)
                    top_price, top_amount = orderbook['asks'][0]
                    print("current top %s @ %s" % (top_amount, top_price))
                except:
                    pass
                time.sleep(NORMAL_WAIT)
            else:
                completed = order['amount']
                total_bought += completed
                print("Completed %s @ %s" % (order['amount'], top_price))
                print("Total %s" % total_bought)
                print()
                time.sleep(WAIT_BETWEEN_TRADES)
                break

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

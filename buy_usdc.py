"""
A simple script that tries to buy an amount of USDC from Pesos
"""
import requests
import sys
import time 
import json
import ccxt

PAIR = "USDC_ARS"
NORMAL_WAIT = 10
WAIT_BETWEEN_TRADES = 30

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
    amount = float(sys.argv[1])
    limit = float(sys.argv[2])
    chunk = float(sys.argv[3])
    config = json.load(open("config.json", "r"))

    print("""CONFIRM:
Buying: %s USDC
Limit price: %s ARS
Chunk size: %s USDC
""" % (amount, limit, chunk))
    if input("confirm y/n: ") == "y":
        print()
        run(amount, limit, chunk, config)

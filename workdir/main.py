import json
import os

from binance.client import Client
import requests


# Get config
symbol = "BNBEUR"
db_url = os.getenv("COUCHDB_BINANCE_BNBEUR_URL")
key = os.getenv("BINANCE_API_KEY")
secret = os.getenv("BINANCE_API_SECRET")

# Keep the views b tree in order
response = requests.get(
    db_url + "/_design/first/_view/time_id?descending=true&limit=1",
)

# Get the latest trade id already in the DB
response = requests.get(
    db_url + "/_design/first/_view/id_trade?descending=true&limit=1",
)
response_json = json.loads(response.text)
fromId = response_json["rows"][0]["key"]

# Get the latest trades from exchange
client = Client(key, secret)
trades = client.get_historical_trades(symbol=symbol, limit=1000, fromId=fromId)
if len(trades) >= 2:
    trades = trades[1:]

    ## Put the latest trades into the DB
    if len(trades) >= 1:
        doc_id = f"{trades[0]['id']}_to_{trades[-1]['id']}"
        response = requests.put(
            db_url + f"/{doc_id}",
            data=json.dumps({"trades": trades}),
        )


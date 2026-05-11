import requests
from config import CRYPTOQUANT_API_KEY

BASE = "https://api.cryptoquant.com/v1/"

def get_metric(metric_path, asset):
    url = f"{BASE}{metric_path}?token={CRYPTOQUANT_API_KEY}&symbol={asset}&limit=1"
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if "data" in data and len(data["data"]) > 0:
                return float(data["data"][0]["value"])
    except Exception as e:
        print(f"Error CryptoQuant {asset}: {e}")
    return None

def get_exchange_inflow(asset):
    return get_metric("exchange-inflow", asset)

def get_exchange_outflow(asset):
    return get_metric("exchange-outflow", asset)

def get_mpi(asset):
    return get_metric("mpi", asset)

def get_ssr(asset):
    return get_metric("ssr", asset)

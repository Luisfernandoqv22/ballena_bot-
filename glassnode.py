import requests
from config import GLASSNODE_API_KEY

BASE = "https://api.glassnode.com/v1/metrics"

def get_metric(metric, asset):
    url = f"{BASE}/{metric}"
    params = {"a": asset, "api_key": GLASSNODE_API_KEY, "f": "json"}
    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if data and len(data) > 0:
                return data[-1]["v"]
    except Exception as e:
        print(f"Error Glassnode: {e}")
    return None

def get_netflow(asset):
    return get_metric("indicators/exchange_net_position_change", asset)

def get_whale_ratio(asset):
    return get_metric("indicators/exchange_whale_ratio", asset)

def get_price(asset):
    return get_metric("market/price_usd_close", asset)

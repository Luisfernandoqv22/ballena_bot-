import requests
from config import WHALE_ALERT_API_KEY, WHALE_TX_MIN_VALUE

BASE = "https://api.whale-alert.io/v1"

def get_whale_transactions(min_value=WHALE_TX_MIN_VALUE, limit=20):
    params = {
        "api_key": WHALE_ALERT_API_KEY,
        "min_value": min_value,
        "limit": limit,
        "cryptocurrency": "bitcoin,ethereum,binance-coin"
    }
    try:
        resp = requests.get(f"{BASE}/transactions", params=params, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("transactions", [])
    except:
        pass
    return []

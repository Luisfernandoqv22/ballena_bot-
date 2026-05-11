from collections import deque
from config import *
from glassnode import get_netflow, get_whale_ratio, get_price
from whale_alert import get_whale_transactions
from cryptoquant import get_exchange_inflow, get_exchange_outflow, get_mpi, get_ssr

state = {}

EXCHANGE_TAGS = [
    "binance", "coinbase", "kraken", "bybit", "okx",
    "huobi", "kucoin", "bitfinex", "gemini", "ftx"
]

def _init(asset):
    if asset not in state:
        state[asset] = {
            "buy_score": deque(maxlen=CONSECUTIVE_DAYS),
            "sell_score": deque(maxlen=CONSECUTIVE_DAYS),
            "raw_data": {}
        }

def analyze(asset):
    _init(asset)
    
    net = get_netflow(asset)
    wh  = get_whale_ratio(asset)
    price = get_price(asset)
    txs = get_whale_transactions()
    inflow = get_exchange_inflow(asset)
    outflow = get_exchange_outflow(asset)
    mpi = get_mpi(asset)
    ssr = get_ssr(asset)

    score_buy = 0.0
    score_sell = 0.0

    if net is not None:
        if net <= NETFLOW_BUY:
            score_buy += WEIGHTS["netflow"]
        elif net >= NETFLOW_SELL:
            score_sell += WEIGHTS["netflow"]

    if wh is not None:
        if wh <= WHALE_RATIO_BUY:
            score_buy += WEIGHTS["whale_ratio"]
        elif wh >= WHALE_RATIO_SELL:
            score_sell += WEIGHTS["whale_ratio"]

    if txs:
        to_ex = 0
        from_ex = 0
        for tx in txs:
            if tx.get("symbol", "").upper() == asset:
                to_addr = tx.get("to", {}).get("address", "").lower()
                from_addr = tx.get("from", {}).get("address", "").lower()
                if any(tag in to_addr for tag in EXCHANGE_TAGS):
                    to_ex += 1
                if any(tag in from_addr for tag in EXCHANGE_TAGS):
                    from_ex += 1
        if from_ex > to_ex:
            score_buy += WEIGHTS["whale_tx"]
        elif to_ex > from_ex:
            score_sell += WEIGHTS["whale_tx"]

    if inflow is not None and outflow is not None:
        net_flow_pct = outflow - inflow
        if net_flow_pct > 0.3:
            score_buy += WEIGHTS["exchange_inout"]
        elif net_flow_pct < -0.3:
            score_sell += WEIGHTS["exchange_inout"]
    elif outflow is not None and inflow is None:
        if outflow > 0.3:
            score_buy += WEIGHTS["exchange_inout"]

    if mpi is not None:
        if mpi <= MPI_BUY:
            score_buy += WEIGHTS["mpi"]
        elif mpi >= MPI_SELL:
            score_sell += WEIGHTS["mpi"]

    if ssr is not None:
        if ssr <= SSR_BUY:
            score_buy += WEIGHTS["ssr"]
        elif ssr >= SSR_SELL:
            score_sell += WEIGHTS["ssr"]

    state[asset]["raw_data"] = {
        "net": net, "wh": wh, "inflow": inflow, "outflow": outflow,
        "mpi": mpi, "ssr": ssr, "txs": len(txs) if txs else 0,
        "score_buy": score_buy, "score_sell": score_sell
    }

    st = state[asset]
    st["buy_score"].append(1 if score_buy >= BUY_THRESHOLD else 0)
    st["sell_score"].append(1 if score_sell >= SELL_THRESHOLD else 0)

    signal = None
    if sum(st["buy_score"]) == CONSECUTIVE_DAYS:
        st["buy_score"].clear()
        st["sell_score"].clear()
        signal = "BUY"
    elif sum(st["sell_score"]) == CONSECUTIVE_DAYS:
        st["buy_score"].clear()
        st["sell_score"].clear()
        signal = "SELL"

    return signal, price, state[asset]["raw_data"]

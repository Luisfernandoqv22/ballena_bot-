import os

# ========== APIs (todas gratuitas, datos reales) ==========
GLASSNODE_API_KEY    = os.getenv("GLASSNODE_API_KEY")
WHALE_ALERT_API_KEY  = os.getenv("WHALE_ALERT_API_KEY")
CRYPTOQUANT_API_KEY  = os.getenv("CRYPTOQUANT_API_KEY")

# ========== TELEGRAM ==========
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

# ========== ACTIVOS ==========
ASSETS = ["BTC", "ETH", "BNB"]

# ========== UMBRALES INDIVIDUALES (datos reales) ==========
NETFLOW_BUY           = -150
NETFLOW_SELL          =  150
WHALE_RATIO_BUY       = 0.80
WHALE_RATIO_SELL      = 0.90
WHALE_TX_MIN_VALUE    = 5_000_000   # $5M

# CryptoQuant umbrales (valores históricos)
EXCHANGE_INFLOW_BUY   = -0.05
EXCHANGE_INFLOW_SELL  =  0.05
MPI_BUY               = 1.0
MPI_SELL              = 2.5
SSR_BUY               = 8
SSR_SELL              = 20

# ========== CONSENSO PONDERADO (escala 0-1) ==========
WEIGHTS = {
    "netflow":       0.25,
    "whale_ratio":   0.20,
    "whale_tx":      0.15,
    "exchange_inout":0.20,
    "mpi":           0.10,
    "ssr":           0.10
}
BUY_THRESHOLD  = 0.65
SELL_THRESHOLD = 0.65
CONSECUTIVE_DAYS = 2

# ========== HORARIOS (UTC) ==========
HORA_LV = "16:00"   # 10:00 AM Monterrey
HORA_SAB = "18:00"  # Mediodía Monterrey

# ========== PUERTO PARA HEALTH CHECK ==========
PORT = int(os.environ.get("PORT", 10000))

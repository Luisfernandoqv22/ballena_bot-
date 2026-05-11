import asyncio
import json
import logging
import os
import schedule
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta
from telegram import Bot
from config import *
from signal_engine import analyze

# ---------- LOGGING ----------
if not os.path.exists("logs"):
    os.makedirs("logs")
logging.basicConfig(
    filename="logs/bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# ---------- TELEGRAM BOT ----------
bot = Bot(token=TELEGRAM_BOT_TOKEN)
REMINDERS_FILE = "pending_reminders.json"

# ---------- HEALTH CHECK SERVER (para UptimeRobot) ----------
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def start_health_server():
    port = PORT
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"💊 Health server en puerto {port}")
    server.serve_forever()

# ---------- RECORDATORIOS ----------
def load_reminders():
    if not os.path.exists(REMINDERS_FILE):
        return []
    with open(REMINDERS_FILE) as f:
        return json.load(f)

def save_reminders(rem):
    with open(REMINDERS_FILE, "w") as f:
        json.dump(rem, f, indent=2)

def add_reminder(asset, price, rtype):
    rems = load_reminders()
    rems = [r for r in rems if not (r["asset"] == asset and r["type"] == rtype)]
    due = (datetime.utcnow() + timedelta(days=7)).isoformat()
    rems.append({
        "asset": asset,
        "price_at_signal": price,
        "due": due,
        "type": rtype,
        "chat_id": TELEGRAM_CHAT_ID
    })
    save_reminders(rems)

# ---------- MENSAJES TELEGRAM ----------
def send_alert(asset, signal, price, raw):
    score_buy = raw["score_buy"]
    score_sell = raw["score_sell"]
    if signal == "BUY":
        emoji = "🟢"
        accion = f"CONVERTIR USDT → {asset}"
        detalle = (
            f"✅ <b>Consenso de ballenas (Score: {score_buy:.2f}/{sum(WEIGHTS.values()):.2f})</b>\n"
            f"• Flujo neto (Glassnode): {raw['net']:,.0f} (retirada)\n"
            f"• Whale Ratio: {raw['wh']:.2f}\n"
            f"• Transacciones ballena (>$5M): {raw['txs']} detectadas\n"
            f"• Exchange Inflow/Outflow (CryptoQuant): {raw['inflow']} / {raw['outflow']}\n"
            f"• MPI (mineros): {raw['mpi']:.2f}\n"
            f"• SSR (poder stablecoin): {raw['ssr']:.2f}\n"
            "→ Fase de acumulación real confirmada."
        )
        pct = "🔹 <b>Convierte el 70% de tu USDT</b>"
        rtype = "buy_second"
    else:
        emoji = "🔴"
        accion = f"CONVERTIR {asset} → USDT"
        detalle = (
            f"✅ <b>Consenso de ballenas (Score: {score_sell:.2f}/{sum(WEIGHTS.values()):.2f})</b>\n"
            f"• Flujo neto (Glassnode): {raw['net']:,.0f} (depósito)\n"
            f"• Whale Ratio: {raw['wh']:.2f}\n"
            f"• Transacciones ballena (>$5M): {raw['txs']} detectadas\n"
            f"• Exchange Inflow/Outflow (CryptoQuant): {raw['inflow']} / {raw['outflow']}\n"
            f"• MPI (mineros): {raw['mpi']:.2f}\n"
            f"• SSR (poder stablecoin): {raw['ssr']:.2f}\n"
            "→ Fase de distribución real confirmada."
        )
        pct = "🔹 <b>Convierte entre el 50% y 75% de tu posición</b>"
        rtype = "sell_second"

    texto = (
        f"{emoji} <b>SEÑAL REAL ON‑CHAIN - {asset}</b>\n"
        f"<b>Acción manual:</b> {accion}\n"
        f"<b>Precio actual:</b> ${price:,.2f}\n\n"
        f"{detalle}\n\n{pct}\n\n"
        f"⏰ <i>En 7 días analizaré la segunda parte.</i>"
    )
    asyncio.run(bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto, parse_mode='HTML'))
    logger.info(f"Señal {signal} {asset} enviada. Score={score_buy if signal=='BUY' else score_sell}")
    add_reminder(asset, price, rtype)

def send_reminder(rem):
    asset = rem["asset"]
    price_old = rem["price_at_signal"]
    rtype = rem["type"]
    signal, price, raw = analyze(asset)
    if price is None:
        price_str = "N/D"
    else:
        price_str = f"${price:,.2f}"

    if rtype == "buy_second":
        titulo = "RECORDATORIO 30% RESTANTE"
        if signal == "BUY":
            rec = "✅ Acumulación real continúa. Convierte el 30%."
        elif signal == "SELL":
            rec = "⚠️ Distribución detectada. No conviertas ahora."
        else:
            rec = "ℹ️ Sin datos concluyentes. Tú decides."
    else:
        titulo = "RECORDATORIO VENTA RESTANTE"
        if signal == "SELL":
            rec = "✅ Distribución real continúa. Convierte el resto."
        elif signal == "BUY":
            rec = "⚠️ Acumulación detectada. No vendas ahora."
        else:
            rec = "ℹ️ Sin datos concluyentes. Tú decides."

    texto = (
        f"⏰ <b>{titulo} - {asset}</b>\n"
        f"Precio hace 7 días: ${price_old:,.2f}\n"
        f"Precio actual: {price_str}\n\n{rec}"
    )
    asyncio.run(bot.send_message(chat_id=rem["chat_id"], text=texto, parse_mode='HTML'))
    logger.info(f"Recordatorio {rtype} {asset} enviado")

# ---------- TAREA DIARIA ----------
def job():
    logger.info("Análisis diario con datos reales")
    print(f"--- Análisis {datetime.utcnow()} UTC ---")
    for asset in ASSETS:
        signal, price, raw = analyze(asset)
        if signal and price:
            send_alert(asset, signal, price, raw)
    rems = load_reminders()
    now = datetime.utcnow()
    updated = []
    for r in rems:
        if datetime.fromisoformat(r["due"]) <= now:
            send_reminder(r)
        else:
            updated.append(r)
    save_reminders(updated)

# ---------- ARRANQUE ----------
if __name__ == "__main__":
    logger.info("Bot v5.0 + health server iniciado")
    print("🤖 Bot ballenas datos reales v5.0 – consenso ponderado")
    print(f"📊 Activos: {', '.join(ASSETS)}")
    print(f"💊 Health server activo en puerto {PORT}")

    # Iniciar servidor HTTP en un hilo separado
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    # Programar análisis
    schedule.every().monday.at(HORA_LV).do(job)
    schedule.every().tuesday.at(HORA_LV).do(job)
    schedule.every().wednesday.at(HORA_LV).do(job)
    schedule.every().thursday.at(HORA_LV).do(job)
    schedule.every().friday.at(HORA_LV).do(job)
    schedule.every().saturday.at(HORA_SAB).do(job)

    while True:
        schedule.run_pending()
        time.sleep(60)

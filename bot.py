import asyncio
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import xml.etree.ElementTree as ET

# Servidor HTTP para mantener el plan gratuito en Render
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def start_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheck)
    server.serve_forever()

# Credenciales
TELEGRAM_BOT_TOKEN = "8294462874:AAE9K4iwnBl2DBJ2TjA9ldcylIwC-x3ejPQ"
TELEGRAM_CHAT_ID = "-4334361804"

# Feed de noticias macroeconómicas y renta fija
RSS_URL = "https://news.google.com/rss/search?q=US+Treasury+OR+Fed+OR+PCE+OR+CPI+OR+Bessent&hl=en-US&gl=US&ceid=US:en"

last_guid = None

def enviar_telegram(titulo, enlace):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"📰 **[NUEVA NOTICIA MACRO]**\n\n{titulo}\n\n🔗 {enlace}",
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            print("✅ Noticia enviada a Telegram exitosamente.")
        else:
            print(f"❌ Error de Telegram ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"❌ Error al enviar a Telegram: {e}")

async def main():
    global last_guid
    print("🚀 Monitor Macro iniciado en Render Free Tier...")

    while True:
        try:
            response = requests.get(RSS_URL, timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                item = root.find(".//channel/item")
                
                if item is not None:
                    guid = item.find("guid").text
                    title = item.find("title").text
                    link = item.find("link").text
                    
                    if guid != last_guid:
                        if last_guid is not None:
                            print(f"🔔 Nuevo titular detectado: {title[:50]}...")
                            enviar_telegram(title, link)
                        else:
                            print("📌 Conectado al feed. Esperando nuevos titulares...")
                        
                        last_guid = guid
        except Exception as e:
            print(f"⚠️ Alerta en búsqueda: {e}")
            
        await asyncio.sleep(30)

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    asyncio.run(main())

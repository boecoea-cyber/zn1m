import asyncio
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from twikit import Client

# Servidor HTTP básico para mantener el servicio gratis en Render
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
TELEGRAM_BOT_TOKEN = "8276776398:AAFPAsmft-yF7_MqniQXpm380pSIaV8_Ze0"
TELEGRAM_CHAT_ID = "-4334361804"
TWITTER_USER = "financialjuice"

client = Client('en-US')
last_tweet_id = None

def enviar_telegram(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"📰 **[NUEVA NOTICIA MACRO]**\n\n{texto}",
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
    global last_tweet_id
    print("🚀 Monitor iniciado en Render Free Tier...")

    while True:
        try:
            user = await client.get_user_by_screen_name(TWITTER_USER)
            tweets = await user.get_tweets('Tweets', count=1)
            
            if tweets:
                latest_tweet = tweets[0]
                
                if latest_tweet.id != last_tweet_id:
                    if last_tweet_id is not None:
                        print(f"🔔 Nuevo titular: {latest_tweet.text[:50]}...")
                        enviar_telegram(latest_tweet.text)
                    else:
                        print("📌 Conectado. Esperando noticias...")
                    
                    last_tweet_id = latest_tweet.id
                    
        except Exception as e:
            print(f"⚠️ Alerta en búsqueda: {e}")
            
        await asyncio.sleep(30)

if __name__ == "__main__":
    # Arrancar puerto web en segundo plano
    threading.Thread(target=start_server, daemon=True).start()
    # Ejecutar monitor
    asyncio.run(main())

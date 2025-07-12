import logging
import requests
import schedule
import time
from bs4 import BeautifulSoup
from telegram import Bot
import random

# ----------------- CONFIGURAZIONE --------------------

TELEGRAM_BOT_TOKEN = '8036580370:AAESwh9z2iAuXIt2NlBCJ-We8CSyDs3vPUI'
CHANNEL_USERNAME = '@offertelampoamazonetemu'
AMAZON_TRACKING_ID = 'consigliere-21'

# ----------------- FINE CONFIGURAZIONE --------------------

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_BOT_TOKEN)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept-Language': 'it-IT,it;q=0.9'
}

def get_lightning_deals():
    url = 'https://www.amazon.it/gp/goldbox'
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    deals = []
    for deal in soup.select('.DealContent'):
        try:
            title = deal.select_one('.DealTitle').get_text(strip=True)
            link = 'https://www.amazon.it' + deal.select_one('a')['href']
            # Aggiungiamo tracking ID
            if '?' in link:
                link += f'&tag={AMAZON_TRACKING_ID}'
            else:
                link += f'?tag={AMAZON_TRACKING_ID}'

            price_span = deal.select_one('.a-price .a-offscreen')
            price = price_span.get_text(strip=True) if price_span else 'Prezzo non disponibile'
            deals.append({
                'title': title,
                'link': link,
                'price': price
            })
        except Exception as e:
            logging.warning(f"Errore parsing: {e}")
            continue

    return deals

def post_random_deal():
    logging.info("Cerco offerte lampo Amazon.it...")
    deals = get_lightning_deals()
    if not deals:
        logging.warning("Nessuna offerta trovata.")
        return

    deal = random.choice(deals)
    message = f"🔥 {deal['title']}\n💶 {deal['price']}\n👉 [Acquista ora]({deal['link']})"

    try:
        bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode='Markdown')
        logging.info(f"Offerta pubblicata: {deal['title']}")
    except Exception as e:
        logging.error(f"Errore nell'invio al canale: {e}")

# Avvia bot ogni 15 minuti
schedule.every(15).minutes.do(post_random_deal)

print("🤖 Bot in esecuzione... (CTRL+C per fermarlo)")
while True:
    schedule.run_pending()
    time.sleep(1)

"""
-------------------------------------------
Ввести в терминале:
    1. pip install telegram-send
    2. telegram-send --configure
    3. вставить токен из BotFather
https://www.youtube.com/watch?v=-73hRicngD8
-------------------------------------------
"""
import telegram_send

def send_telegram(text):
    telegram_send.send(messages=[text])

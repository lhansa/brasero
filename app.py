import os
import json
import requests

def send_telegram(MENSAJE):

    TOKEN = os.environ['TELEGRAM_TOKEN']
    CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

    full_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "text": MENSAJE
    }

    try:
        with requests.post(full_url, data=params) as response:
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Mensaje enviado correctamente a Telegram"})
            }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

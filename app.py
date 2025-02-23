from src import get_forecast
from src import send_telegram

codigo_municipio = "28079"  # Código de Madrid, por ejemplo
api_key = os.getenv('AEMET_KEY')
manana_date = datetime.date.today() + datetime.timedelta(days=1)


message_with_forecast = get_forecast(codigo_municipio, manana_date, api_key)
send_telegram(message_with_forecast)
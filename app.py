import os
import datetime
import json
import requests

# from utils.get_forecast import get_forecast
# from utils.send_telegram import send_telegram

def get_forecast(codigo_municipio, forecast_date, api_key):
    # Calcular la fecha de mañana en formato YYYY-MM-DD
    manana = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    
    # URL de la API de AEMET para predicción diaria
    url_prediccion = f"https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/{codigo_municipio}"
    headers = {
      "accept": "application/json",
      "api_key": api_key
    }
    
    respuesta = requests.get(url_prediccion, headers=headers).json()
    if (respuesta['estado'] != 200):
        raise ConnectionError('AEMET call did not work')
    
    datos_url = respuesta['datos']
    print('URL with data: ' + datos_url)

    datos_prediccion = requests.get(datos_url).json()
    
    manana_str = forecast_date.isoformat()
        
    # Extraer los datos de mañana
    for prediccion in datos_prediccion:
        for dia in prediccion.get("prediccion", {}).get("dia", []):
            fecha_dia = dia.get("fecha", "")[:10] 
            if fecha_dia == manana_str:
                temperatura_min = dia.get("temperatura", {}).get("minima")
                temperatura_max = dia.get("temperatura", {}).get("maxima")
                estado_cielo = dia.get("estadoCielo", [{}])[0].get("descripcion", "No disponible")
    
    
                # Formatear la fecha en estilo "24 de febrero"
                fecha_formateada = forecast_date.strftime("%-d")
                
                mensaje = f"🌤**Previsión del tiempo**\nMañana día {fecha_formateada} la temperatura mínima será {temperatura_min}°C, la máxima {temperatura_max}°C. \nEstado del cielo: {estado_cielo}."
                print('Mensaje creado:\n' + mensaje)
                return(mensaje)
            

def send_telegram(MENSAJE):

    TOKEN = os.getenv('TELEGRAM_TOKEN')
    CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

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

codigo_municipio = "28079"  # Código de Madrid, por ejemplo
api_key = os.getenv('AEMET_KEY')
manana_date = datetime.date.today() + datetime.timedelta(days=1)


message_with_forecast = get_forecast(codigo_municipio, manana_date, api_key)
send_telegram(message_with_forecast)

# if __name__ == "__main__":
    
#     codigo_municipio = "28079"  # Código de Madrid, por ejemplo
#     api_key = os.getenv('AEMET_KEY')
#     manana_date = datetime.date.today() + datetime.timedelta(days=1)
    
    
#     message_with_forecast = get_forecast(codigo_municipio, manana_date, api_key)
#     send_telegram(message_with_forecast)
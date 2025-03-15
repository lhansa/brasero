import os
import datetime
import json
import requests

# from utils.get_forecast import get_forecast
# from utils.send_telegram import send_telegram

def get_forecast(codigo_municipio, forecast_date, api_key):
    
    url_prediccion = f"https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/{codigo_municipio}"
    headers = {
      "accept": "application/json",
      "api_key": api_key
    }
    
    respuesta = requests.get(url_prediccion, headers=headers).json()
    if (respuesta['estado'] != 200):
        raise ConnectionError('AEMET call did not work for code ' + codigo_municipio)
    
    datos_url = respuesta['datos']

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

                mensaje = f"Temperatura: mín {temperatura_min}°C, máx {temperatura_max}°C. \nCielo: {estado_cielo}."

    return(mensaje)
                
def create_message(dict_msg, forecast_date):
                
    mensaje_final = "🌤🌤 **Previsión del tiempo** 🌤🌤\n\n"
    
    fecha_formateada = forecast_date.strftime("%-d/%m")

    mensaje_final = mensaje_final + f"📅 {fecha_formateada}\n\n"
    mensaje_final = mensaje_final + "\n\n".join(f"**{key}**\n{message}" for key, message in dict_msg.items())
    
    print('Mensaje final creado')
    return(mensaje_final)
            

def send_telegram(MENSAJE):

    TOKEN = os.getenv('TELEGRAM_TOKEN')
    CHAT_ID = os.getenv('TELEGRAM_CHAT_ID2')
    print(CHAT_ID)

    full_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "text": MENSAJE, 
        "parse_mode": "Markdown"
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

api_key = os.getenv('AEMET_KEY')
manana_date = datetime.date.today() + datetime.timedelta(days=1)

msg_madrid = get_forecast('28079', manana_date, api_key)
msg_colmenar = get_forecast('28045', manana_date, api_key)

dict_with_messages = {
    '🏢 Madrid' : msg_madrid, 
    '🏡 Colmenar': msg_colmenar
}

message_with_forecasts = create_message(dict_with_messages, manana_date)

send_telegram(message_with_forecasts)

# if __name__ == "__main__":
    
#     codigo_municipio = "28079"  # Código de Madrid, por ejemplo
#     api_key = os.getenv('AEMET_KEY')
#     manana_date = datetime.date.today() + datetime.timedelta(days=1)
    
    
#     message_with_forecast = get_forecast(codigo_municipio, manana_date, api_key)
#     send_telegram(message_with_forecast)
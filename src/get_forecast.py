import requests
import datetime
import os

def get_forecast(codigo_municipio, api_key):
    # Calcular la fecha de mañana en formato YYYY-MM-DD
    manana = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    
    # URL de la API de AEMET para predicción diaria
    url_prediccion = f"https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/{codigo_municipio}"
    headers = {
      "accept": "application/json",
      "api_key": api_key
    }
    
    # Obtener la URL con los datos
    respuesta = requests.get(url_prediccion, headers=headers)
    datos_url = respuesta.json()

    return(datos_url)
    
   

# Ejemplo de uso
codigo_municipio = "28079"  # Código de Madrid, por ejemplo
api_key = os.getenv('AEMET_KEY')

resultado1 = get_forecast(codigo_municipio, api_key)

print(resultado1)




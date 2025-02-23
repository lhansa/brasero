import requests
import datetime

def get_forecast(codigo_municipio, api_key):
    # Calcular la fecha de mañana en formato YYYY-MM-DD
    manana = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    
    # URL de la API de AEMET para predicción diaria
    url_prediccion = f"https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/{codigo_municipio}/?api_key={api_key}"
    
    # Obtener la URL con los datos
    respuesta = requests.get(url_prediccion)
    datos_url = respuesta.json().get('datos')
    
    if not datos_url:
        return "Error al obtener la URL de datos."
    
    # Descargar los datos desde la URL proporcionada
    datos_prediccion = requests.get(datos_url).json()
    
    # Extraer los datos de mañana
    for prediccion in datos_prediccion:
        for dia in prediccion.get("prediccion", {}).get("dia", []):
            if dia.get("fecha") == manana:
                temperatura_min = dia.get("temperatura", {}).get("minima")
                temperatura_max = dia.get("temperatura", {}).get("maxima")
                estado_cielo = dia.get("estadoCielo", [{}])[0].get("descripcion", "No disponible")
                
                return {
                    "fecha": manana,
                    "temperatura_minima": temperatura_min,
                    "temperatura_maxima": temperatura_max,
                    "estado_cielo": estado_cielo
                }
    
    return "No hay datos disponibles para mañana."

# Ejemplo de uso
codigo_municipio = "28079"  # Código de Madrid, por ejemplo
api_key = '$AEMET_KEY'
print(get_forecast(codigo_municipio, api_key))

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
                
                mensaje = f"Mañana día {fecha_formateada} la temperatura mínima será {temperatura_min}°C, la máxima {temperatura_max}°C. \n Estado del cielo: {estado_cielo}."
                print('Mensaje creado:\n' + mensaje)
                return(mensaje)
            
import os
import sys
import time
import datetime
import requests

AEMET_URL = "https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/{}"
MAX_INTENTOS = 5
TIMEOUT = 30


def _get_json_con_reintentos(url, headers=None, descripcion=""):
    """GET + JSON con reintentos y backoff. AEMET falla a menudo de forma
    intermitente (429 por límite de peticiones, 5xx, cuerpo vacío...)."""
    espera = 5
    ultimo_error = None
    for intento in range(1, MAX_INTENTOS + 1):
        try:
            r = requests.get(url, headers=headers, timeout=TIMEOUT)
            if r.status_code == 200 and r.text.strip():
                datos = r.json()
                # La primera llamada de AEMET devuelve 'estado' dentro del JSON
                if isinstance(datos, dict) and "estado" in datos and datos["estado"] != 200:
                    ultimo_error = f"estado={datos.get('estado')} descripcion={datos.get('descripcion')}"
                else:
                    return datos
            else:
                ultimo_error = f"HTTP {r.status_code} cuerpo={r.text[:200]!r}"
        except (requests.RequestException, ValueError) as e:
            ultimo_error = f"{type(e).__name__}: {e}"

        print(f"[{descripcion}] intento {intento}/{MAX_INTENTOS} fallido: {ultimo_error}")
        if intento < MAX_INTENTOS:
            time.sleep(espera)
            espera *= 2

    raise ConnectionError(f"[{descripcion}] AEMET no respondió tras {MAX_INTENTOS} intentos: {ultimo_error}")


def get_forecast(codigo_municipio, forecast_date, api_key):
    headers = {"accept": "application/json", "api_key": api_key}

    respuesta = _get_json_con_reintentos(
        AEMET_URL.format(codigo_municipio), headers, f"{codigo_municipio} metadatos"
    )
    datos_prediccion = _get_json_con_reintentos(
        respuesta["datos"], descripcion=f"{codigo_municipio} datos"
    )

    fecha_str = forecast_date.isoformat()
    for prediccion in datos_prediccion:
        for dia in prediccion.get("prediccion", {}).get("dia", []):
            if dia.get("fecha", "")[:10] == fecha_str:
                temperatura_min = dia.get("temperatura", {}).get("minima")
                temperatura_max = dia.get("temperatura", {}).get("maxima")
                estado_cielo = dia.get("estadoCielo", [{}])[0].get("descripcion") or "No disponible"
                return f"Temperatura: mín {temperatura_min}°C, máx {temperatura_max}°C. \nCielo: {estado_cielo}."

    raise ValueError(f"No hay predicción para {fecha_str} en el municipio {codigo_municipio}")


def create_message(dict_msg, forecast_date):
    mensaje_final = "🌤🌤 *Previsión del tiempo* 🌤🌤\n\n"
    mensaje_final += f"📅 {forecast_date.strftime('%-d/%m')}\n\n"
    mensaje_final += "\n\n".join(f"*{key}*\n{message}" for key, message in dict_msg.items())
    print("Mensaje final creado")
    return mensaje_final


def send_telegram(mensaje):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID2")

    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"},
        timeout=TIMEOUT,
    )
    if not r.ok:
        raise ConnectionError(f"Telegram respondió HTTP {r.status_code}: {r.text[:300]}")
    print("Mensaje enviado a Telegram")


if __name__ == "__main__":
    api_key = os.getenv("AEMET_KEY")
    manana_date = datetime.date.today() + datetime.timedelta(days=1)

    municipios = {
        "🏡 Colmenar": "28045",
        "🏘️ Alcobendas": "28006",
        "🏢 Madrid": "28079",
    }

    mensajes = {}
    fallos = 0
    for nombre, codigo in municipios.items():
        try:
            mensajes[nombre] = get_forecast(codigo, manana_date, api_key)
        except Exception as e:
            print(f"ERROR en {nombre}: {e}")
            mensajes[nombre] = "Predicción no disponible ahora mismo."
            fallos += 1
        time.sleep(2)  # no machacar a AEMET con ráfagas de peticiones

    if fallos == len(municipios):
        sys.exit("Ningún municipio se pudo obtener de AEMET; no se envía mensaje.")

    send_telegram(create_message(mensajes, manana_date))

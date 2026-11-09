# Recon Tool — Escáner de Reconocimiento Automatizado

Script de reconocimiento que combina escaneo de red con Nmap y
búsqueda automática de vulnerabilidades conocidas (CVEs) usando
la API oficial del NVD (National Vulnerability Database).

## Qué hace

1. Escanea un host o rango de red con Nmap (detección de versiones)
2. Extrae el CPE (Common Platform Enumeration) de cada servicio detectado
3. Convierte el CPE de formato 2.2 a 2.3 (requerido por la API del NVD)
4. Busca automáticamente los CVEs asociados a cada CPE en el NVD
5. Presenta un reporte estructurado de hallazgos, diferenciando entre
   "sin CVEs encontrados" y "error en la búsqueda"

## Requisitos

- Python 3
- Nmap instalado en el sistema
- Librerías: `python-nmap`, `requests`
- API key gratuita del NVD: https://nvd.nist.gov/developers/request-an-api-key

## Instalación

```bash
pip install python-nmap requests --break-system-packages
```

## Uso

```bash
python3 recon_tool.py <tu-nvd-api-key>
```

El script solicitará la IP o rango objetivo de forma interactiva.

**Para un solo host:**
```
IP a escanear: 192.168.1.10
```
Escanea todos los puertos (`-p-`) con detección de versiones (`-sV`).

**Para un rango de red (CIDR):**
```
IP a escanear: 192.168.1.0/24
```
Ofrece un menú con dos modos:
- **Descubrimiento de hosts** (`-sn`): identifica qué hosts están activos
  sin escanear puertos, ideal como primer paso en una red grande
- **Escaneo completo**: puertos y versiones de todos los hosts del rango

## Ejemplo de salida

```
Puerto 80: open - http Apache httpd 2.2.8

CVEs:

Buscando CVEs para Apache httpd 2.2.8...
CVEs encontrados: CVE-2007-4723, CVE-2007-6420, CVE-2008-0455,
CVE-2008-0456, CVE-2008-2364, CVE-2008-2939, CVE-2009-0796,
CVE-2009-1195, CVE-2009-0023, CVE-2009-1955
```

## Diseño técnico

- **API key manejada por argumento de línea de comandos**, nunca
  hardcodeada en el código — evita exponerla al subir el script a
  repositorios públicos como GitHub.
- **Conversión CPE 2.2 → 2.3**: Nmap devuelve CPEs en formato 2.2
  (`cpe:/a:vendor:product:version`), pero la API del NVD requiere
  formato 2.3 con 11 campos fijos. El script realiza esta conversión
  y valida que los campos obligatorios (part, vendor, product, version)
  estén presentes antes de consultar la API.
- **Manejo diferenciado de resultados**: la función de búsqueda
  devuelve una tupla `[éxito, dato]` para distinguir claramente entre
  "la búsqueda funcionó pero no hay CVEs conocidos" y "la búsqueda
  falló por un error" (timeout, CPE incompleto, límite de rate, etc.)
- **Rate limiting respetado**: pausa de 1 segundo entre peticiones
  a la API usando una API key autenticada (límite de 50 peticiones
  cada 30 segundos según documentación del NVD).

## Advertencia legal

Esta herramienta debe usarse únicamente contra sistemas donde se
tiene autorización explícita. El escaneo no autorizado de redes
ajenas es ilegal.

## Autor
Miguel Marín — desarrollado como parte del curso de Red Team / Offensive Security

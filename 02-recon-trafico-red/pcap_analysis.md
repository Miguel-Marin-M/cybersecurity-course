# Análisis de PCAP — Tráfico HTTP Real

## Archivo analizado
`http_sample.pcap` — captura de ejemplo de Wireshark (tráfico real de 2007)

---

## Protocolos identificados

| Protocolo | Descripción |
|---|---|
| HTTP | Tráfico web sin cifrar — el más relevante para el análisis |
| TCP | Protocolo de transporte — permite ver el ciclo completo de la conexión |
| MDNS | Protocolo de descubrimiento de dispositivos en red local |
| ICMPv6 | Protocolo de diagnóstico de red (versión IPv6) |

**Total de paquetes:** 55
**Paquetes HTTP:** 2 (1 request + 1 response)
**Paquetes TCP:** 10 (incluye los de HTTP)

---

## Análisis del stream TCP — Ciclo completo de la conexión

Al seguir el stream TCP se pudo reconstruir la conversación completa:

SYN → Cliente inicia la conexión con el servidor
SYN-ACK → Servidor acepta la conexión
ACK → Conexión establecida
GET / → Cliente solicita la página raíz (request HTTP)
200 OK → Servidor responde con contenido HTML
FIN, ACK → Cliente cierra la conexión de forma ordenada
ACK → Servidor confirma el cierre

**Diferencia clave observada:**
- `FIN` → cierre limpio y ordenado (comportamiento normal)
- `RST` → cierre abrupto (indica firewall, rechazo o herramienta de escaneo)

---

## Análisis del tráfico HTTP

### Request (lo que envió el cliente)

GET / HTTP/1.0
Host: cl-1985.ham-01.de.sixxs.net
User-Agent: Lynx/2.8.6rel.2 libwww-FM/2.14 SSL-MM/1.4.1 OpenSSL/0.9.8b
Accept-Language: en

**Hallazgo:** el cliente usó **Lynx**, un navegador de línea de comandos
— no un navegador gráfico convencional. Esto es visible para cualquier
persona que capture el tráfico.

### Response (lo que devolvió el servidor)

HTTP/1.1 200 OK
Server: Apache
Content-Type: text/html

---

## Vulnerabilidades identificadas

### 1. Information Disclosure — Versión del servidor expuesta
**Severidad:** Media

El header `Server: Apache` revela que el servidor usa Apache.
En un entorno real se reportaría la versión exacta para buscar
CVEs asociados. Exponer la versión del servidor le da al atacante
información para seleccionar exploits específicos.

**Remediación:** configurar el servidor para ocultar o falsificar
el header `Server`.

### 2. Directory Listing Enabled
**Severidad:** Alta

El servidor devolvió la estructura completa de sus carpetas y archivos
sin requerir autenticación. Cualquier visitante puede ver qué hay
en el servidor. En esta captura se encontraron directorios con nombres
sensibles (`cia/`, `bnd/`, `korrupt/`) expuestos públicamente.

**Remediación:** deshabilitar el directory listing en la configuración
del servidor web (`Options -Indexes` en Apache).

---

## Lección principal

Todo este contenido fue legible porque viajó en **HTTP sin cifrar**.
Con **HTTPS**, los paquetes serían visibles en Wireshark pero el
contenido estaría cifrado — ilegible para un atacante en la misma red.

HTTP sin cifrar en redes corporativas es un hallazgo que siempre
se incluye en un reporte de pentest real.

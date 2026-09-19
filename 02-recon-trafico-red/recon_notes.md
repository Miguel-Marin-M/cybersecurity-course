# Módulo 2 — Reconocimiento y Análisis de Tráfico de Red

## Herramientas usadas
- Nmap 7.99
- Wireshark 4.6.6
- TryHackMe (VPN via OpenVPN TCP)

---

## Escaneo de reconocimiento — Máquina TryHackMe

### Escaneo básico
```bash
nmap -Pn <IP>
```
Resultado: 5 puertos abiertos, 995 filtrados. Sistema identificado como Windows.

### Escaneo con detección de versiones
```bash
nmap -Pn -sV <IP>
```

| Puerto | Servicio | Versión |
|---|---|---|
| 21 | FTP | FileZilla ftpd 0.9.60 beta |
| 53 | DNS | Simple DNS Plus |
| 80 | HTTP | Microsoft IIS httpd 10.0 |
| 135 | MSRPC | Microsoft Windows RPC |
| 3389 | RDP | Microsoft Terminal Services |

### Detección de sistema operativo
```bash
sudo nmap -Pn -sV -O <IP>
```
Resultado: Windows Server 2019 (92% confianza)

### Hallazgos y riesgos

| Hallazgo | Riesgo |
|---|---|
| RDP expuesto (puerto 3389) | Alto — vector común de fuerza bruta |
| FTP en versión beta (0.9.60) | Medio — software no apto para producción |
| Servidor web IIS 10.0 | Medio — superficie de ataque web |
| DNS expuesto (puerto 53) | Medio — posible zone transfer |

---

## Análisis de tráfico con Wireshark

**Interfaz capturada:** tun0 (túnel VPN TryHackMe)
**Total de paquetes capturados:** 2144

### Filtros aplicados

| Filtro | Resultado | Qué muestra |
|---|---|---|
| `tcp.flags.syn == 1` | 2044 paquetes | Patrón de escaneo de puertos |
| `tcp.flags.syn == 1 && tcp.flags.ack == 1` | 27 paquetes | Puertos que respondieron (abiertos) |
| `tcp.port == 80` | 70 paquetes | Conversación completa con servidor web |

### Three-way handshake observado en puerto 80
- **SYN** → Kali inicia conexión con el servidor
- **SYN-ACK** → Servidor confirma que el puerto está abierto
- **ACK** → Kali completa la conexión

Los RST observados al inicio corresponden a paquetes per0didos
por latencia (Colombia → Virginia, EE.UU.) que Nmap reintentó
automáticamente.

### Conclusión del análisis
Un escaneo Nmap genera ~2044 paquetes SYN en pocos segundos —
patrón fácilmente detectable por un IDS/SIEM como actividad
anómala. En un entorno real, este volumen de SYN desde una
sola IP en poco tiempo dispararía una alerta automática.

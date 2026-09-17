# Teoría de Redes

## TCP — Transmission Control Protocol

Protocolo de comunicación que garantiza que los datos lleguen correctamente
entre dos dispositivos. Antes de intercambiar datos, establece una conexión
mediante el **Three-Way Handshake**:

- **SYN** → El dispositivo llama al servidor ("quiero conectarme")
- **SYN-ACK** → El servidor responde ("recibí tu solicitud, aquí estoy")
- **ACK** → El dispositivo confirma ("entendido, empecemos")

Solo después de estos 3 pasos se intercambian datos reales.

---

## Comandos de red en Linux

- `ip a` → Lista todas las interfaces de red del equipo y sus direcciones IP asignadas
- `ip route` → Muestra la tabla de enrutamiento: qué camino toma el tráfico según su destino, incluyendo el gateway hacia internet
- `cat /etc/resolv.conf` → Muestra qué servidor DNS usa el sistema para convertir nombres de dominio (como google.com) en direcciones IP

---

## CIDR — Notación de redes

Forma de expresar un rango de direcciones IP. El número después del `/`
indica cuántos bits son fijos (la red) y cuántos son variables (los dispositivos).

| Notación | Dispositivos disponibles | Uso típico |
|---|---|---|
| `/8` | ~16 millones | Redes de ISPs |
| `/16` | ~65,000 | Redes corporativas grandes |
| `/24` | 254 | Redes domésticas u oficinas |
| `/32` | 1 solo dispositivo | Apuntar a un host específico |

Ejemplo: `192.168.1.0/24` → red fija en `192.168.1`, dispositivos del `.1` al `.254`

---

## Mi red local

Resultado del análisis con `ip a`, `ip route` y `cat /etc/resolv.conf`:

Internet
|
Router / Gateway (192.168.1.254)
|
|--- Kali Linux - Máquina local (192.168.1.53)
|--- Otros dispositivos (192.168.1.x)

Interno solamente:
Docker (172.17.0.1) → contenedores de laboratorio (Módulos 2 en adelante)

**DNS configurado:** servidores del ISP
- `<DNS_primario>`
- `<DNS_secundario>`

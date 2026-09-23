# SQL Injection Labs — PortSwigger Web Security Academy

## Lab 1 — SQL injection en WHERE clause

**Vulnerabilidad:** SQL Injection en parámetro `category`
**Objetivo:** recuperar productos ocultos (released=0)

**Consulta original del servidor:**
```sql
SELECT * FROM productos WHERE category='Gifts' AND released=1
```

**Payload usado:**

/filter?category=Gifts'+OR+1=1--+-

**Cómo funciona el payload:**
- `'` → cierra el string abierto por la app
- `OR 1=1` → condición siempre verdadera, devuelve todos los registros
- `--+-` → comenta el resto de la consulta (elimina el filtro `released=1`)

**Resultado:** la app devolvió todos los productos incluyendo los ocultos

**Impacto en escenario real:** un atacante podría acceder a productos,
datos o registros que la aplicación oculta intencionalmente — precios
especiales, usuarios inactivos, datos de otras empresas en un sistema
multitenant.

**Remediación:** usar consultas parametrizadas (prepared statements)
en vez de concatenar el input del usuario directamente en el SQL.

## Lab 2 — Login bypass via SQL Injection

**Vulnerabilidad:** SQL Injection en formulario de login
**Objetivo:** acceder como administrador sin conocer la contraseña

**Consulta original del servidor:**
```sql
SELECT * FROM usuarios WHERE username='input' AND password='input'
```

**Payload usado:**
- Username: `administrator'--`
- Password: cualquier valor

**Consulta resultante:**
```sql
SELECT * FROM usuarios WHERE username='administrator'--' AND password='...'
```

**Cómo funciona:**
`'` cierra el string del username y `--` comenta el resto de la
consulta, eliminando completamente la validación de contraseña.
El servidor solo verifica que el usuario exista.

**Impacto en escenario real:** acceso total a cuentas de administrador
sin necesidad de credenciales — uno de los ataques más críticos
posibles en una aplicación web.

**Remediación:** prepared statements y nunca concatenar input
del usuario directamente en consultas SQL.

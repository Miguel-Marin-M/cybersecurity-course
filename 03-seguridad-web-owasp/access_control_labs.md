# Access Control Labs — PortSwigger Web Security Academy

Colección de laboratorios prácticos de Broken Access Control completados
en PortSwigger Web Security Academy. Los labs cubren técnicas de escalación
horizontal y vertical, IDOR y bypass de controles de acceso.

---

## Lab 1 — Unprotected admin functionality

**Vulnerabilidad:** Panel de administración accesible sin autenticación
**Objetivo:** encontrar y acceder al panel admin para eliminar al usuario carlos

### Técnica usada
Revisión del archivo `robots.txt` — archivo público que indica a los
motores de búsqueda qué rutas no indexar. Irónicamente, expone
exactamente las rutas que el administrador quiere mantener ocultas.

### Cómo funciona
```
/robots.txt → revela ruta del panel admin → acceso directo sin autenticación
```

### Resultado
Panel de administración accesible directamente desde la URL.
Usuario carlos eliminado. Lab resuelto.

### Impacto en escenario real
Cualquier atacante revisa `robots.txt` como primer paso de reconocimiento.
Un panel admin sin autenticación es acceso total al sistema.

### Remediación
- Nunca depender de la oscuridad como mecanismo de seguridad
- Implementar autenticación en todas las rutas administrativas
- No listar rutas sensibles en `robots.txt`

---

## Lab 2 — Unprotected admin functionality with unpredictable URL

**Vulnerabilidad:** Ruta admin oculta expuesta en código fuente del cliente
**Objetivo:** encontrar la ruta admin sin que esté en `robots.txt`

### Técnica usada
Inspección del código fuente del navegador — el JavaScript de la página
contenía un script que habilitaba dinámicamente un enlace al panel
administrativo, revelando la ruta en el código del cliente.

### Cómo funciona
```javascript
// Código fuente del navegador revelaba algo como:
if (isAdmin) {
    document.getElementById('adminLink').href = '/ruta-secreta-admin';
}
```
Aunque la ruta sea "impredecible", cualquier usuario puede verla
inspeccionando el JavaScript que se envía al navegador.

### Resultado
Ruta admin encontrada en el código fuente. Panel accesible sin
autenticación. Lab resuelto.

### Impacto en escenario real
El código JavaScript se envía completo al navegador de cualquier usuario.
Nunca debe contener rutas, tokens o lógica de seguridad sensible.

### Remediación
- Nunca incluir rutas administrativas en código JavaScript del cliente
- Implementar autenticación server-side en todas las rutas admin
- La lógica de autorización siempre debe vivir en el servidor

---

## Lab 3 — User role controlled by request parameter

**Vulnerabilidad:** Rol de usuario controlado por cookie modificable
**Objetivo:** escalar privilegios de usuario normal a administrador

### Tipo de ataque
Escalación vertical — acceder a funciones de un nivel superior al propio.

### Técnica usada
Interceptar el request con Burp Suite al intentar acceder a `/admin`.
La cookie `Admin=false` controlaba el nivel de acceso — modificarla
a `Admin=true` otorgó acceso completo al panel.

### Cómo funciona
```
Cookie: Admin=false → interceptar con Burp → Cookie: Admin=true → acceso admin
```

El servidor confiaba ciegamente en el valor de una cookie del cliente
para determinar el nivel de acceso, sin verificarlo contra la sesión
en el servidor.

### Resultado
Acceso completo al panel de administración. Lab resuelto.

### Impacto en escenario real
Cualquier usuario puede modificar cookies con Burp Suite o las
DevTools del navegador. Nunca debe usarse una cookie del cliente
para determinar roles o permisos.

### Remediación
- Los roles deben almacenarse y verificarse en el servidor (sesión/BD)
- Nunca confiar en datos del cliente para decisiones de autorización
- Implementar verificación de permisos server-side en cada request

---

## Lab 4 — User ID controlled by request parameter

**Vulnerabilidad:** IDOR en parámetro de URL
**Objetivo:** acceder a los datos de otro usuario manipulando el parámetro ID

### Tipo de ataque
Escalación horizontal — acceder a datos de otro usuario del mismo nivel.

### Técnica usada
Al iniciar sesión, la URL del perfil contenía el parámetro `id=wiener`.
Cambiar el parámetro a `id=carlos` devolvió el perfil completo de ese
usuario, incluyendo su API key.

### Cómo funciona
```
/my-account?id=wiener → cambiar parámetro → /my-account?id=carlos → datos de carlos
```

El servidor usaba el parámetro de la URL para determinar qué usuario
mostrar, sin verificar que el usuario autenticado tuviera permiso
para ver esos datos.

### Resultado
Acceso a los datos y API key del usuario carlos. Lab resuelto.

### Impacto en escenario real
En aplicaciones reales esto permite acceder a datos personales, historial
de compras, mensajes privados o cualquier recurso de cualquier usuario
simplemente cambiando un número en la URL.

### Remediación
- Verificar en el servidor que el usuario autenticado es dueño
  del recurso solicitado antes de mostrarlo
- No usar IDs predecibles para recursos sensibles
- Implementar controles de acceso a nivel de objeto

---

## Lab 5 — User ID controlled by request parameter with unpredictable user IDs

**Vulnerabilidad:** IDOR con IDs no predecibles (GUIDs)
**Objetivo:** encontrar el ID de otro usuario cuando no es un número secuencial

### Tipo de ataque
Escalación horizontal con IDs tipo GUID (identificadores únicos no predecibles).

### Técnica usada
Aunque el ID no era predecible, fue encontrado en las publicaciones
del blog — el nombre del autor era un enlace que incluía el ID del
usuario como parámetro en la URL.

### Proceso
```
1. Buscar publicaciones del blog escritas por carlos
2. El nombre "carlos" tenía un enlace con su GUID en la URL
3. Usar ese GUID en /my-account?id=<GUID-de-carlos>
4. Acceso a sus datos
```

### Por qué usar GUIDs no es suficiente
Los IDs no predecibles reducen la superficie de ataque pero no la
eliminan. Si el ID se expone en algún otro lugar de la aplicación
(perfiles públicos, comentarios, posts), un atacante puede encontrarlo.

### Resultado
GUID de carlos encontrado en sus publicaciones del blog.
Acceso a sus datos. Lab resuelto.

### Impacto en escenario real
Demuestra que la oscuridad no es seguridad — un ID difícil de adivinar
sigue siendo explotable si se filtra en otro lugar de la aplicación.

### Remediación
- IDs no predecibles son una capa de defensa, no la única
- Implementar verificación de ownership server-side en cada request
- Auditar todos los lugares donde se exponen IDs de usuarios

---

## Lab 6 — URL-based access control can be circumvented

**Vulnerabilidad:** Control de acceso basado en URL bypasseable via headers
**Objetivo:** acceder al panel admin bypasseando el bloqueo de la URL `/admin`

### Técnica usada
El servidor bloqueaba requests directos a `/admin`, pero procesaba
el header `X-Original-URL` para determinar la ruta real a servir.
Enviar el request a `/` con el header `X-Original-URL: /admin`
bypasseó el control de acceso.

### Cómo funciona
```http
GET / HTTP/1.1
X-Original-URL: /admin
```

El firewall o middleware verificaba la URL del request (`/`) y la
permitía. El servidor backend leía `X-Original-URL` para determinar
qué servir, ignorando que el control de acceso ya había pasado.

### Por qué este header existe
`X-Original-URL` es usado en arquitecturas con proxies o load balancers
para preservar la URL original del cliente. Cuando el backend lo procesa
sin verificar permisos, crea este bypass.

### Resultado
Acceso al panel de administración bypasseando el control de la URL.
Lab resuelto.

### Impacto en escenario real
Headers como `X-Original-URL`, `X-Forwarded-For`, `X-Rewrite-URL`
son vectores de bypass comunes en arquitecturas con múltiples capas.
Un WAF que filtra por URL puede ser bypasseado si el backend procesa
estos headers.

### Remediación
- Implementar controles de acceso en el backend, no solo en el perímetro
- Deshabilitar el procesamiento de `X-Original-URL` si no es necesario
- Nunca confiar en headers del cliente para decisiones de seguridad

---

## Lab 7 — Multi-step process with flawed access control at one step

**Vulnerabilidad:** Control de acceso verificado solo en el primer paso
de un proceso de múltiples pasos
**Objetivo:** escalar privilegios saltando la verificación del paso 1

### Tipo de ataque
Escalación vertical — acceder a funciones de administrador desde
una cuenta de usuario normal.

### Proceso de explotación
```
1. Autenticarse como administrator y completar el flujo de upgrade
   de usuario → capturar el request del paso 2 con Burp
2. Autenticarse como wiener (usuario normal)
3. Intentar el request del paso 1 con la cookie de wiener → error 403
4. Enviar directamente el request del paso 2 con la cookie de wiener
   → éxito, privilegios escalados
```

### Por qué funciona
El servidor verificaba autorización en el paso 1, pero asumía que
cualquier request al paso 2 ya había pasado por el paso 1 correctamente.
No volvía a verificar permisos en el paso 2.

### Cómo funciona
```
Paso 1: /admin/upgrade → verifica permisos → bloqueado para wiener
Paso 2: /admin/upgrade/confirm → NO verifica permisos → accesible para wiener
```

### Resultado
Privilegios de administrador otorgados a cuenta de usuario normal
saltando la verificación del paso 1. Lab resuelto.

### Impacto en escenario real
Flujos de múltiples pasos (checkout, cambio de rol, aprobaciones)
deben verificar autorización en cada paso independientemente —
nunca asumir que llegar al paso N implica haber sido autorizado
en los pasos anteriores.

### Remediación
- Verificar autorización en cada paso del flujo de forma independiente
- No asumir que el estado del flujo implica autorización previa
- Implementar tokens de estado server-side para flujos multi-paso

---

## Resumen — Tipos de Access Control vulnerabilities

| Tipo | Técnica | Impacto |
|---|---|---|
| Escalación vertical | Acceder a rutas admin sin auth | Control total del sistema |
| Escalación vertical | Modificar cookie de rol | Acceso a funciones de admin |
| Escalación horizontal (IDOR) | Modificar ID en URL | Datos de cualquier usuario |
| Escalación horizontal (IDOR) | Encontrar GUID filtrado | Datos de usuario específico |
| Bypass de URL | Header X-Original-URL | Evadir controles perimetrales |
| Multi-step bypass | Saltar paso con verificación | Escalar privilegios parcialmente |

## Lección principal
El control de acceso siempre debe verificarse **server-side** en
cada request, independientemente de:
- Lo que diga el cliente (cookies, parámetros, headers)
- El paso del flujo en que se encuentre el usuario
- Si la URL parece "impredecible" u "oculta"

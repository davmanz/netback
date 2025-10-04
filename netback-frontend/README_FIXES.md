# Netback Frontend — Bugs & Fixes

Este documento centraliza los **problemas detectados** en `netback-frontend` y la **hoja de ruta de correcciones** con *diffs* y comprobaciones de QA.  
Objetivo: reforzar **consistencia, seguridad, manejo de errores** y **DX**.

---

## 🧭 Cómo usar este documento

1. Abre un PR por cada sección (o agrúpalas por temática).
2. Copia/pega los *diffs* sugeridos.
3. Ejecuta el checklist de QA de cada fix.
4. Cierra la casilla ✅ en la tabla de seguimiento.

---

## 📋 Resumen de issues

| # | Título | Impacto | Estado |
|---|---|---|---|
| 1 | PropTypes incorrectos en `DeviceTable` | Warning/bug de runtime | ☐ |
| 2 | Token duplicado (`sessionStorage` vs `localStorage`) | Inconsistencia de auth | ☐ |
| 3 | Cliente HTTP inconsistente (`axios`/`fetch` vs `apiClient`) | Errores irregulares | ☐ |
| 4 | Manejo de errores “silencioso” en `api.js` | UX confusa | ☐ |
| 5 | Merge de backups por campo posiblemente incorrecto | Datos erróneos en Dashboard | ☐ |
| 6 | Import/export inconsistente de `ConfirmDialog` | Build/runtime inconsistente | ☐ |
| 7 | `useIsSmallScreen` accede a `window` al inicializar | SSR/robustez | ☐ |
| 8 | Workbox instalado pero SW desactivado | Build innecesaria | ☐ |
| 9 | `client_max_body_size` bajo para CSV grandes | Fallos en importación | ☐ |
| 10 | CSP: `connect-src` con `localhost:8080` innecesario | Endurecimiento | ☐ |
| 11 | Doble lockfile (npm y pnpm) | Ruido en builds | ☐ |

---

## 1) `DeviceTable` – PropTypes incorrectos

**Síntoma**  
El componente usa la prop `openBackupClick`, pero `propTypes` declara `onBackupClick`.

**Fix**
```diff
// src/components/Dashboard/DeviceTable.js
- DeviceTable.propTypes = {
-   devices: PropTypes.array.isRequired,
-   onBackupClick: PropTypes.func.isRequired,
-   onMenuClick: PropTypes.func.isRequired,
- };
+ DeviceTable.propTypes = {
+   devices: PropTypes.array.isRequired,
+   openBackupClick: PropTypes.func.isRequired,
+   onMenuClick: PropTypes.func.isRequired,
+ };
```

**QA**
- [ ] Abrir Dashboard y verificar que el botón “Ver Respaldo” abre el modal sin warnings.

---

## 2) `Login` — token duplicado

**Síntoma**  
`login()` guarda JWT en `localStorage`, pero `Login.js` también guarda en `sessionStorage`.

**Fix**
```diff
// src/pages/Login.js
- sessionStorage.setItem("token", data.access);
```

**QA**
- [ ] Iniciar sesión, refrescar y confirmar que sigues autenticado.
- [ ] Cerrar sesión: verificar que se limpian las claves de `localStorage`.

---

## 3) Unificar cliente HTTP con `apiClient`

**Síntoma**  
`api.js` mezcla `axios` y `fetch` y no usa los interceptores de `apiClient` (manejo 401, timeout, baseURL).

**Patrón de cambio**
- Importa `apiClient`.
- Quita `API_URL` y los `headers` manuales (el interceptor pone el `Bearer`).
- Reemplaza `fetch/axios` por `apiClient`.

**Ejemplos**
```diff
- import axios from "axios";
+ import apiClient from "./apiClient";

- const response = await axios.get(`${API_URL}/users/`, { headers: { Authorization: `Bearer ${token}` } });
+ const response = await apiClient.get(`/users/`);

- const response = await fetch(`${API_URL}/networkdevice/`, { headers: { Authorization: `Bearer ${token}` }});
- let devices = await response.json();
+ const { data: devices } = await apiClient.get(`/networkdevice/`);
```

**QA**
- [ ] Forzar 401 (token inválido): debe redirigir al login automáticamente.
- [ ] Ver que todas las pantallas (usuarios, equipos, backups) cargan sin errores de CORS/headers.

---

## 4) Estandarizar manejo de errores en `api.js`

**Síntoma**  
Muchas funciones devuelven `[]` o `null` en error → la UI cree “no hay datos”.

**Fix (patrón A: lanzar errores)**
```js
// Ejemplo: getUsers
export const getUsers = async () => {
  const { data } = await apiClient.get(`/users/`);
  return data; // si falla, lanzará y lo capturas en la página
};
```

**Fix (patrón B: contrato uniforme)**
```js
// wrapper
const ok = (data) => ({ ok: true, data });
const fail = (err) => ({ ok: false, error: err?.message || "Error desconocido" });

// Ejemplo: getUsers
export const getUsers = async () => {
  try {
    const { data } = await apiClient.get(`/users/`);
    return ok(data);
  } catch (e) {
    return fail(e);
  }
};
```

**QA**
- [ ] Simular caída de API: UI debe mostrar `Snackbar/Alert` claro (no tablas vacías engañosas).

---

## 5) Unión de backups en `useDevices`

**Síntoma**  
La unión se hace con `b.id === device.id`. Si el endpoint devuelve `device_id`, fallará.

**Fix**
```diff
// src/hooks/useDevices.js
- const backup = backupsData.find((b) => b.id === device.id);
+ const backup = backupsData.find((b) => (b.device_id ?? b.id) === device.id);
```

**QA**
- [ ] Ver que “Última Modif.” y el acceso a “Ver Respaldo” reflejan el último backup real.

---

## 6) `ConfirmDialog` — import/export consistente

**Síntoma**  
Unos archivos usan `export default`, otros `export { ConfirmDialog }`.

**Fix recomendado**
- En `components/common/ConfirmDialog.jsx` exporta **default**:
  ```js
  export default function ConfirmDialog(...) { ... }
  ```
- En todos los consumidores:
  ```diff
  - import { ConfirmDialog } from "../components/common/ConfirmDialog";
  + import ConfirmDialog from "../components/common/ConfirmDialog";
  ```

**QA**
- [ ] Confirmaciones en Users/Vault/DeviceManagement funcionan y sin warnings de importación.

---

## 7) `useIsSmallScreen` — acceso a `window` seguro

**Síntoma**  
Accede a `window` en el estado inicial (no SSR-safe; pequeño hardening).

**Fix**
```diff
// src/hooks/useIsSmallScreen.js
- const [isSmallScreen, setIsSmallScreen] = useState(window.innerWidth < breakpoint);
+ const [isSmallScreen, setIsSmallScreen] = useState(() =>
+   typeof window !== "undefined" ? window.innerWidth < breakpoint : false
+ );
```

**QA**
- [ ] La app sigue respondiendo a `resize` y no lanza errores en tests/headless.

---

## 8) Workbox instalado pero SW desactivado

**Síntoma**  
Dockerfile instala Workbox, pero el frontend **unregister** del service worker. Build innecesaria.

**Fix (simplificar)**
```diff
# Dockerfile
- RUN pnpm add \
-     workbox-precaching \
-     workbox-core \
-     workbox-routing \
-     workbox-strategies \
-     workbox-expiration
```
*(Opcional alternativo: activar PWA registrando el SW, pero requiere ajustar CSP y estrategia de cache.)*

**QA**
- [ ] Imagen más rápida de construir, sin cambios funcionales.

---

## 9) Nginx — `client_max_body_size` para CSV grandes

**Síntoma**  
Importaciones masivas pueden superar 10M.

**Fix**
```diff
# nginx.conf (bloque http)
- client_max_body_size 10M;
+ client_max_body_size 50M;
```

**QA**
- [ ] Subir CSV grande (>10M) sin 413.

---

## 10) CSP — `connect-src` endurecido

**Síntoma**  
CSP incluye `http://localhost:8080`. Si todo va a `/api` en el mismo dominio, basta `'self'`.

**Fix**
```diff
Content-Security-Policy:
- connect-src 'self' http://localhost:8080;
+ connect-src 'self';
```
> Si en desarrollo llamas directamente a `http://localhost:8080`, conserva esa entrada sólo en el entorno de dev.

**QA**
- [ ] Navegar app y verificar que no hay bloqueos CSP en consola.

---

## 11) Lockfiles duplicados

**Síntoma**  
Existen `pnpm-lock.yaml` y `package-lock.json`.

**Fix**
- Estándar: **pnpm** (coincide con Dockerfile).
- Borrar `package-lock.json`.
- Añadir a `.gitignore` si es necesario.

**QA**
- [ ] Build local y en CI reproducibles con `pnpm i && pnpm build`.

---

## 🔐 Recomendaciones de seguridad (opcional, plan futuro)

- Migrar JWT a **cookies httpOnly + SameSite=Lax/Strict** para reducir riesgo XSS.
- Añadir `helmet` en el proxy y nonces/hashes CSP para eliminar `'unsafe-inline'` en `style-src` cuando sea viable.

---

## ✅ Checklist de verificación global

- [ ] Login/Logout con expiración/401 → redirección automática a `/`.
- [ ] Dashboard: estados de backup correctos, sin warnings.
- [ ] Users: CRUD + confirmación de borrado.
- [ ] Devices: crear/editar/eliminar; CSV export OK.
- [ ] Backups: historial, ver detalle, forzar backup (ping OK/KO).
- [ ] Compare: selección exacta de 2 backups → diffs.
- [ ] Bulk import: CSV/Zabbix, filtros, selección por página y global, guardado masivo.
- [ ] Sites/Areas: validaciones y creación OK.
- [ ] Programación de respaldo: validación HH:MM y confirmación.

---

## 🧱 Notas de implementación

- Considera migrar a **TypeScript** y/o **TanStack Query** para cacheo y estados de red.
- Centraliza shapes de datos (normaliza `snake_case`/`camelCase` en el cliente o en el proxy).
- Añade tests E2E (Cypress) para flujos críticos.


## ✅ Checklist de acciones

1. Corregir `executor.py` (`vaultCredential`) y revalidar ejecución de comandos.
2. Alinear `BackupStatusTracker` y estados en `backup.py` (`success`/`unchanged`/`error`).
3. Quitar validaciones en `perform_create/update` y delegarlas al serializer.
4. Definir estrategia única para Celery Beat (DBScheduler + PeriodicTask **o** `beat_schedule` en código).
5. Eliminar `app:/app` en `docker-compose.yml` (o reemplazar por `/app/data`).
6. Añadir `/health/` al proxy y ajustar healthchecks.
7. Corregir `TIME_ZONE` y revisar `ALLOWED_HOSTS`/CORS.
8. Simplificar `SiteSerializer`/`AreaSerializer`.
9. **Opcional:** Cifrar `customPass` con `Fernet` (requiere migración).
10. **Opcional:** Endurecer CSP y ajustar rate limiting en Nginx.

---

## 🧪 Pruebas mínimas tras cambios

- **Backend:** `pytest`/`manage.py test` (si aplica) + `curl /api/health/` → **200**.
- **Proxy:** `curl :8080/health/` → `{ "status": "ok" }`.
- **Celery:** Logs de `celery-beat` y `celery` ejecutando `autoBackup` en la frecuencia esperada.
- **Frontend:** Navegar SPA y verificar llamadas `/api/*` a través del proxy.

---

## Observaciones finales

La base del sistema es sólida. Los tres defectos críticos detectados afectaban **persistencia segura**, **ejecución remota** y **programación de tareas**.
Con las correcciones propuestas, la plataforma queda más **robusta**, **segura** y **predecible** en operación.

# Guía de Capturas de Pantalla - Mesa 24/7 Backend Challenge

Esta guía te indica exactamente qué capturas tomar y con qué nombre guardarlas.

## 📁 Ubicación

Guarda todas las capturas en: `docs/screenshots/`

---

## 📸 Lista de Capturas

### 1. `01-swagger-ui-overview.png`
**Qué capturar:** Página principal de Swagger UI
- URL: http://localhost:8000/docs
- Muestra todos los endpoints organizados por secciones
- Captura completa mostrando: processor, restaurants, payouts, health

**Cómo tomarlo:**
- Abre http://localhost:8000/docs en tu navegador
- Haz scroll hasta arriba para ver el título "Mesa247 Backend Challenge"
- Captura toda la página (puedes hacer scroll y tomar múltiples capturas si es necesario)

---

### 2. `02-post-event-201-created.png`
**Qué capturar:** Respuesta exitosa al crear un evento nuevo (201 Created)
- Endpoint: POST /v1/processor/events
- Debe mostrar **Code: 201**

**Cómo tomarlo:**
1. En Swagger UI, click en "POST /v1/processor/events"
2. Click en "Try it out"
3. Usa este JSON (evento NUEVO con ID diferente):
```json
{
  "event_id": "evt_screenshot_new_2025",
  "event_type": "charge_succeeded",
  "occurred_at": "2025-12-30T22:00:00Z",
  "restaurant_id": "res_002",
  "currency": "USD",
  "amount": 50000,
  "fee": 2500
}
```
4. Click "Execute"
5. Captura la respuesta mostrando **Code: 201** y el response body

---

### 3. `03-post-event-200-idempotency.png`
**Qué capturar:** Respuesta de idempotencia (200 OK - evento duplicado)
- Endpoint: POST /v1/processor/events
- Debe mostrar **Code: 200** con mensaje "already_processed"

**Cómo tomarlo:**
1. Usa exactamente el MISMO JSON del paso anterior
2. Click "Execute" de nuevo
3. Captura la respuesta mostrando **Code: 200** y mensaje "Event already processed"

---

### 4. `04-get-balance-simple.png`
**Qué capturar:** Consulta de balance de un restaurante
- Endpoint: GET /v1/restaurants/{restaurant_id}/balance
- Debe mostrar **Code: 200** con balance calculado

**Cómo tomarlo:**
1. En Swagger UI, click en "GET /v1/restaurants/{restaurant_id}/balance"
2. Click en "Try it out"
3. Parámetros:
   - restaurant_id: `res_001`
   - currency: `PEN`
4. Click "Execute"
5. Captura la respuesta mostrando el balance (should be alto ya que cargaste 70 eventos)

---

### 5. `05-get-balance-multiple-currencies.png`
**Qué capturar:** Balance de otro restaurante con diferente moneda
- Endpoint: GET /v1/restaurants/{restaurant_id}/balance

**Cómo tomarlo:**
1. Mismo endpoint
2. Parámetros:
   - restaurant_id: `res_002`
   - currency: `USD`
3. Click "Execute"
4. Captura la respuesta

---

### 6. `06-event-loader-success.png`
**Qué capturar:** Output del script de carga de eventos
- Terminal mostrando los 70 eventos cargados

**Cómo tomarlo:**
- Ya ejecutaste `python scripts/load_events.py`
- Captura tu terminal mostrando:
  - Los 70 eventos procesados
  - El summary final: "Total events: 70, Successful: 70"

---

### 7. `07-docker-containers-running.png`
**Qué capturar:** Contenedores Docker corriendo

**Cómo tomarlo:**
En tu terminal de Ubuntu:
```bash
docker-compose ps
```
Captura el output mostrando el contenedor PostgreSQL en estado "Up (healthy)"

---

### 8. `08-api-health-check.png`
**Qué capturar:** Endpoint de health check

**Cómo tomarlo:**
1. En Swagger UI, click en "GET /health"
2. Click en "Try it out"
3. Click "Execute"
4. Captura la respuesta mostrando status OK

---

### 9. `09-uvicorn-running.png`
**Qué capturar:** Terminal con uvicorn corriendo

**Cómo tomarlo:**
- Captura tu terminal donde corre uvicorn mostrando:
  - "Uvicorn running on http://127.0.0.1:8000"
  - "Application startup complete"
  - Logs de requests procesados

---

### 10. `10-pytest-results.png` (OPCIONAL)
**Qué capturar:** Resultados de los tests

**Cómo tomarlo:**
En tu terminal:
```bash
pytest -v
```
Captura el output (aunque algunos fallen, muestra que tienes tests)

---

## 📋 Checklist

Después de tomar las capturas, verifica que tengas:

- [ ] 01-swagger-ui-overview.png
- [ ] 02-post-event-201-created.png
- [ ] 03-post-event-200-idempotency.png
- [ ] 04-get-balance-simple.png
- [ ] 05-get-balance-multiple-currencies.png
- [ ] 06-event-loader-success.png
- [ ] 07-docker-containers-running.png
- [ ] 08-api-health-check.png
- [ ] 09-uvicorn-running.png
- [ ] 10-pytest-results.png (opcional)

---

## 🎯 Próximo Paso

Una vez que tengas todas las capturas guardadas en `docs/screenshots/`, actualizaremos el README.md para incluir estas imágenes y hacer el commit final al repositorio.

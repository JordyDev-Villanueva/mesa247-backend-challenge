# Guía de Ejecución - Mesa 24/7 Backend Challenge

Esta guía te mostrará paso a paso cómo ejecutar el proyecto por primera vez.

## Opción 1: Con Docker (Recomendado)

### Prerrequisitos
- Python 3.11+
- Docker Desktop para Windows
- Git

### Pasos

#### 1. Verificar que Docker esté corriendo
```bash
docker --version
docker-compose --version
```

#### 2. Crear y activar entorno virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Deberías ver (venv) en tu terminal
```

#### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 4. Iniciar base de datos PostgreSQL
```bash
# Iniciar solo el servicio de base de datos
docker-compose up -d db

# Verificar que esté corriendo
docker-compose ps
```

Deberías ver algo como:
```
NAME                COMMAND                  SERVICE             STATUS
mesa247-db          "docker-entrypoint.s…"   db                  running
```

#### 5. Ejecutar migraciones de base de datos
```bash
# Esto crea las 4 tablas en PostgreSQL
alembic upgrade head
```

Salida esperada:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, initial migration create all tables
```

#### 6. Iniciar la aplicación FastAPI
```bash
uvicorn app.main:app --reload
```

Salida esperada:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### 7. Abrir documentación Swagger
Abre tu navegador en: **http://localhost:8000/docs**

Deberías ver la interfaz Swagger UI con todos los endpoints.

#### 8. Cargar datos de prueba (Opcional)
En otra terminal (manteniendo uvicorn corriendo):
```bash
# Activar el entorno virtual primero
venv\Scripts\activate

# Cargar los 70 eventos de prueba
python scripts/load_events.py
```

Salida esperada:
```
Loading events from events/events.jsonl...
Loaded 70 events

Processing events...
✓ evt_001 | 201 Created
✓ evt_002 | 201 Created
...

Summary:
--------
Total events: 70
Successfully processed: 70
Already existed: 0
Failed: 0
```

#### 9. Probar endpoints manualmente

**Opción A: Desde Swagger UI (http://localhost:8000/docs)**
1. Click en "POST /v1/processor/events"
2. Click en "Try it out"
3. Usa este ejemplo:
```json
{
  "event_id": "evt_manual_test_001",
  "event_type": "charge_succeeded",
  "occurred_at": "2025-12-30T10:00:00Z",
  "restaurant_id": "res_001",
  "currency": "PEN",
  "amount": 10000,
  "fee": 500
}
```
4. Click "Execute"
5. Deberías ver respuesta 201 Created

**Opción B: Desde terminal con curl**
```bash
curl -X POST "http://localhost:8000/v1/processor/events" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_curl_test",
    "event_type": "charge_succeeded",
    "occurred_at": "2025-12-30T10:00:00Z",
    "restaurant_id": "res_001",
    "currency": "PEN",
    "amount": 10000,
    "fee": 500
  }'
```

#### 10. Consultar balance de restaurante
En Swagger UI o con curl:
```bash
curl "http://localhost:8000/v1/restaurants/res_001/balance?currency=PEN"
```

Respuesta esperada:
```json
{
  "restaurant_id": "res_001",
  "currency": "PEN",
  "available": 9500,
  "pending": 0,
  "last_event_at": "2025-12-30T10:00:00Z"
}
```

#### 11. Ejecutar tests
```bash
# En terminal con entorno virtual activado
pytest -v

# Con cobertura
pytest --cov=app
```

Salida esperada:
```
tests/test_api/test_processor.py::test_charge_succeeded_event PASSED
tests/test_api/test_processor.py::test_event_idempotency PASSED
...
========== 8 passed in 2.45s ==========
```

#### 12. Detener todo cuando termines
```bash
# Detener uvicorn: CTRL+C en la terminal

# Detener base de datos
docker-compose down
```

---

## Opción 2: Con PostgreSQL Local (Sin Docker)

### Prerrequisitos
- Python 3.11+
- PostgreSQL 15+ instalado localmente
- Git

### Pasos

#### 1. Crear base de datos
Abre pgAdmin o psql y ejecuta:
```sql
CREATE DATABASE mesa247_challenge;
CREATE USER mesa247_user WITH PASSWORD 'mesa247_pass';
GRANT ALL PRIVILEGES ON DATABASE mesa247_challenge TO mesa247_user;
```

#### 2. Configurar variable de entorno
```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql+asyncpg://mesa247_user:mesa247_pass@localhost:5432/mesa247_challenge"

# Windows CMD
set DATABASE_URL=postgresql+asyncpg://mesa247_user:mesa247_pass@localhost:5432/mesa247_challenge
```

O crear archivo `.env` en la raíz del proyecto:
```
DATABASE_URL=postgresql+asyncpg://mesa247_user:mesa247_pass@localhost:5432/mesa247_challenge
```

#### 3. Continuar desde Paso 2 de Opción 1
El resto de pasos son idénticos (crear venv, instalar deps, ejecutar migrations, etc.)

---

## Endpoints Disponibles

### 1. Health Check
```
GET http://localhost:8000/health
```

### 2. Ingerir Evento
```
POST http://localhost:8000/v1/processor/events
```

### 3. Consultar Balance
```
GET http://localhost:8000/v1/restaurants/{restaurant_id}/balance?currency=PEN
```

### 4. Generar Payouts
```
POST http://localhost:8000/v1/payouts/run
```

### 5. Consultar Payout
```
GET http://localhost:8000/v1/payouts/{payout_id}
```

---

## URLs Importantes

- **Swagger UI (Interactiva)**: http://localhost:8000/docs
- **ReDoc (Documentación)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## Solución de Problemas

### Error: "Connection refused" en base de datos
- Verificar que PostgreSQL esté corriendo: `docker-compose ps`
- Reiniciar servicio: `docker-compose restart db`

### Error: "Port 8000 already in use"
- Matar proceso: `taskkill /F /IM python.exe` (Windows)
- O usar otro puerto: `uvicorn app.main:app --reload --port 8001`

### Error: "alembic: command not found"
- Asegurarse de tener el venv activado
- Reinstalar: `pip install alembic`

### Tests fallan
- Verificar que NO tengas uvicorn corriendo (los tests usan su propia base de datos en memoria)
- Reinstalar dependencias: `pip install -r requirements.txt`

---

## Siguiente Paso: Tomar Screenshots

Una vez que tengas todo corriendo, puedes tomar screenshots de:

1. **Swagger UI** (http://localhost:8000/docs)
2. **Respuesta exitosa** de un POST
3. **Tests pasando** (`pytest -v`)
4. **Balance response** de un restaurante

Estas capturas demuestran que el proyecto funciona correctamente.

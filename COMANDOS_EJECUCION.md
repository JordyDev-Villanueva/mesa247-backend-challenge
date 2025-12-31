# Comandos de Ejecución - Mesa 24/7 Backend Challenge
# Para Ubuntu WSL2 con Docker

## PASO A PASO - Copia y pega estos comandos en orden

### 1. Navegar al directorio del proyecto
```bash
cd "/mnt/e/PROYECTO PYTHON PORTAFOLIO/mesa247-backend-challenge"
```

### 2. Verificar que estás en el directorio correcto
```bash
pwd
ls -la
```
Deberías ver los archivos: README.md, docker-compose.yml, requirements.txt, etc.

### 3. Crear entorno virtual de Python
```bash
python3 -m venv venv
```

### 4. Activar el entorno virtual
```bash
source venv/bin/activate
```
Deberías ver `(venv)` al inicio de tu prompt

### 5. Instalar dependencias
```bash
pip install -r requirements.txt
```
Esto instalará FastAPI, SQLAlchemy, Alembic, etc. (~1-2 minutos)

### 6. Iniciar PostgreSQL con Docker
```bash
docker-compose up -d db
```
Output esperado:
```
Creating network "mesa247-backend-challenge_default" with the default driver
Creating mesa247-db ... done
```

### 7. Verificar que PostgreSQL está corriendo
```bash
docker-compose ps
```
Deberías ver:
```
NAME                COMMAND                  STATUS
mesa247-db          "docker-entrypoint..."   Up
```

### 8. Esperar 5 segundos para que PostgreSQL esté listo
```bash
sleep 5
```

### 9. Ejecutar migraciones (crear las 4 tablas)
```bash
alembic upgrade head
```
Output esperado:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, initial migration create all tables
```

### 10. Iniciar la aplicación FastAPI
```bash
uvicorn app.main:app --reload
```
Output esperado:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 11. Abrir Swagger UI en tu navegador Windows
Abre Chrome/Edge y ve a:
```
http://localhost:8000/docs
```

### 12. (OPCIONAL) Cargar datos de prueba
En OTRA terminal de Ubuntu (mantén uvicorn corriendo):
```bash
cd "/mnt/e/PROYECTO PYTHON PORTAFOLIO/mesa247-backend-challenge"
source venv/bin/activate
python scripts/load_events.py
```

### 13. Probar un endpoint manualmente
Desde Swagger UI o con curl en otra terminal:
```bash
curl -X POST "http://localhost:8000/v1/processor/events" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_test_manual",
    "event_type": "charge_succeeded",
    "occurred_at": "2025-12-30T10:00:00Z",
    "restaurant_id": "res_001",
    "currency": "PEN",
    "amount": 10000,
    "fee": 500
  }'
```

### 14. Consultar balance
```bash
curl "http://localhost:8000/v1/restaurants/res_001/balance?currency=PEN"
```

### 15. Ejecutar tests (en otra terminal)
```bash
cd "/mnt/e/PROYECTO PYTHON PORTAFOLIO/mesa247-backend-challenge"
source venv/bin/activate
pytest -v
```

### 16. Detener todo cuando termines
```bash
# Detener uvicorn: CTRL+C en la terminal donde corre

# Detener PostgreSQL:
docker-compose down
```

---

## SCREENSHOTS RECOMENDADOS

Una vez que todo esté corriendo, toma capturas de:

1. **Swagger UI**: http://localhost:8000/docs (muestra todos los endpoints)
2. **POST exitoso**: Ejecuta un evento y captura la respuesta 201
3. **GET balance**: Muestra el balance calculado correctamente
4. **Tests pasando**: `pytest -v` mostrando todos los tests en verde
5. **Terminal con uvicorn**: Mostrando que la app está corriendo

---

## SOLUCIÓN DE PROBLEMAS

### Error: "port 8000 already in use"
```bash
# Ver qué proceso usa el puerto
sudo lsof -i :8000

# O cambiar de puerto
uvicorn app.main:app --reload --port 8001
```

### Error: "Cannot connect to Docker daemon"
```bash
# Iniciar Docker service
sudo service docker start
```

### Error: alembic no encontrado
```bash
# Asegurarse de tener venv activado
source venv/bin/activate

# Reinstalar
pip install alembic
```

### Error en migraciones
```bash
# Si algo salió mal, reiniciar:
docker-compose down -v  # Elimina volúmenes
docker-compose up -d db
sleep 5
alembic upgrade head
```

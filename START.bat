@echo off
REM =============================================================================
REM Mesa 24/7 Backend Challenge - Script de Inicio Rápido (Windows)
REM =============================================================================

echo.
echo ========================================
echo Mesa 24/7 Backend Challenge
echo Script de Inicio Automatico
echo ========================================
echo.

REM Verificar si el entorno virtual existe
if not exist "venv\" (
    echo [1/6] Creando entorno virtual...
    python -m venv venv
) else (
    echo [1/6] Entorno virtual ya existe
)

echo [2/6] Activando entorno virtual...
call venv\Scripts\activate.bat

echo [3/6] Instalando dependencias...
pip install -q -r requirements.txt

echo [4/6] Iniciando base de datos PostgreSQL con Docker...
docker-compose up -d db

echo [5/6] Esperando a que PostgreSQL esté listo...
timeout /t 5 /nobreak >nul

echo [6/6] Ejecutando migraciones...
alembic upgrade head

echo.
echo ========================================
echo LISTO! El proyecto esta configurado
echo ========================================
echo.
echo Para iniciar la aplicacion:
echo   uvicorn app.main:app --reload
echo.
echo Para cargar datos de prueba:
echo   python scripts/load_events.py
echo.
echo Documentacion API:
echo   http://localhost:8000/docs
echo.
echo Para detener la base de datos:
echo   docker-compose down
echo ========================================
echo.

cmd /k

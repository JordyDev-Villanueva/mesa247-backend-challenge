#!/bin/bash
# =============================================================================
# Mesa 24/7 Backend Challenge - Script de Inicio Rápido (Linux/Mac/WSL)
# =============================================================================

echo ""
echo "========================================"
echo "Mesa 24/7 Backend Challenge"
echo "Script de Inicio Automático"
echo "========================================"
echo ""

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "[1/6] Creando entorno virtual..."
    python3 -m venv venv
else
    echo "[1/6] Entorno virtual ya existe"
fi

echo "[2/6] Activando entorno virtual..."
source venv/bin/activate

echo "[3/6] Instalando dependencias..."
pip install -q -r requirements.txt

echo "[4/6] Iniciando base de datos PostgreSQL con Docker..."
docker-compose up -d db

echo "[5/6] Esperando a que PostgreSQL esté listo..."
sleep 5

echo "[6/6] Ejecutando migraciones..."
alembic upgrade head

echo ""
echo "========================================"
echo "¡LISTO! El proyecto está configurado"
echo "========================================"
echo ""
echo "Para iniciar la aplicación:"
echo "  uvicorn app.main:app --reload"
echo ""
echo "Para cargar datos de prueba:"
echo "  python scripts/load_events.py"
echo ""
echo "Documentación API:"
echo "  http://localhost:8000/docs"
echo ""
echo "Para detener la base de datos:"
echo "  docker-compose down"
echo "========================================"
echo ""

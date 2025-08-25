#!/bin/bash

echo "🚀 Iniciando despliegue de Quinielas API..."

# Forzar migraciones
echo "📊 Aplicando migraciones de base de datos..."
python manage.py migrate --noinput

# Verificar estado de migraciones
echo "🔍 Verificando estado de migraciones..."
python manage.py showmigrations

# Crear superusuario si no existe
echo "👤 Verificando superusuario..."
python manage.py createsuperuser --noinput || true

echo "✅ Configuración completada. Iniciando servidor..."
gunicorn quinielas_backend.wsgi
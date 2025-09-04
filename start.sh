#!/bin/bash
<<<<<<< HEAD
python manage.py migrate
python manage.py cargar_equipos
python manage.py createsuperuser --noinput || true
gunicorn quinielas_backend.wsgi
```
// filepath: c:\Users\Brandon CS\Desktop\Proyectos\Quniela\quinielas_backend\start.sh
=======
>>>>>>> c5bf0359c1ba20429cc9e3cad0748a2081b1e7c2

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
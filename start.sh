#!/bin/bash
python manage.py migrate
python manage.py createsuperuser --noinput || true
gunicorn quinielas_backend.wsgi
```
// filepath: c:\Users\Brandon CS\Desktop\Proyectos\Quniela\quinielas_backend\start.sh

El `|| true` evita que falle si el superusuario ya existe.
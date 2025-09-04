# 🧪 Comandos de Testing - Sistema de Notificaciones

## 🚀 Configuración Inicial

### 1. **Instalar Dependencias**
```bash
cd quinielas_backend
pip install -r requirements.txt
```

### 2. **Configurar Variables de Entorno**
```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar .env con tus valores
nano .env
```

### 3. **Ejecutar Migraciones**
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. **Crear Superusuario (para testing)**
```bash
python manage.py createsuperuser
# Usuario: admin
# Email: admin@example.com
# Password: admin123
```

### 5. **Ejecutar Servidor**
```bash
python manage.py runserver
```

## 🔐 Testing de Autenticación

### 1. **Registrar Usuario**
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario_prueba",
    "email": "prueba@example.com",
    "password": "password123"
  }'
```

### 2. **Login y Obtener Token**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario_prueba",
    "password": "password123"
  }'
```

**Respuesta esperada:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 3. **Probar Autenticación**
```bash
# Reemplazar <ACCESS_TOKEN> con el token obtenido
curl -X GET http://localhost:8000/api/test-auth/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## 📱 Testing de FCM Tokens

### 1. **Registrar Token FCM**
```bash
curl -X POST http://localhost:8000/api/fcm-tokens/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "fcm_token": "fcm_token_de_prueba_12345",
    "device_type": "android",
    "plataforma": "android"
  }'
```

### 2. **Listar Tokens del Usuario**
```bash
curl -X GET http://localhost:8000/api/fcm-tokens/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### 3. **Actualizar Token**
```bash
# Reemplazar <TOKEN_ID> con el ID del token
curl -X PUT http://localhost:8000/api/fcm-tokens/<TOKEN_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "dispositivo": "Samsung Galaxy S21",
    "plataforma": "android"
  }'
```

### 4. **Desactivar Token**
```bash
curl -X DELETE http://localhost:8000/api/fcm-tokens/<TOKEN_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## 🏈 Testing de Quinielas

### 1. **Crear Quiniela (Enviará notificación automática)**
```bash
curl -X POST http://localhost:8000/api/quinielas/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Quiniela de Prueba",
    "apuesta_individual": 10.00
  }'
```

### 2. **Unirse a Quiniela (Enviará notificación al creador)**
```bash
# Reemplazar <QUINIELA_ID> con el ID de la quiniela
curl -X POST http://localhost:8000/api/quinielas/<QUINIELA_ID>/unirse/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### 3. **Agregar Partido**
```bash
curl -X POST http://localhost:8000/api/quinielas/<QUINIELA_ID>/partidos/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "equipo_local_id": 1,
    "equipo_visitante_id": 2,
    "fecha": "2025-01-15T19:00:00Z"
  }'
```

### 4. **Ingresar Resultado (Enviará notificación a todos los participantes)**
```bash
# Reemplazar <PARTIDO_ID> con el ID del partido
curl -X POST http://localhost:8000/api/quinielas/<QUINIELA_ID>/partidos/<PARTIDO_ID>/resultado/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "resultado_equipo_id": 1
  }'
```

### 5. **Realizar Elecciones (Enviará notificación al creador)**
```bash
curl -X POST http://localhost:8000/api/elecciones/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "quiniela_id": <QUINIELA_ID>,
    "elecciones": [
      {
        "partido_id": <PARTIDO_ID>,
        "equipo_elegido": 1
      }
    ]
  }'
```

## 🔔 Testing de Notificaciones

### 1. **Notificación de Prueba**
```bash
curl -X POST http://localhost:8000/api/test-notification/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Notificación de Prueba",
    "body": "Esta es una notificación de prueba del sistema"
  }'
```

### 2. **Notificaciones de Fecha Límite (Solo Staff)**
```bash
# Usar credenciales de superusuario
curl -X POST http://localhost:8000/api/notifications/fecha-limite/ \
  -H "Authorization: Bearer <ADMIN_ACCESS_TOKEN>"
```

## 📊 Verificación de Logs

### 1. **Ver Logs del Servidor**
```bash
# En la terminal donde ejecutas runserver
# Los logs de notificaciones aparecerán automáticamente
```

### 2. **Logs Esperados**
```
INFO: Token FCM enviado exitosamente al servidor
INFO: Notificación de nueva quiniela enviada: Quiniela de Prueba
INFO: Notificación de nuevo participante enviada a usuario_prueba
INFO: Notificación enviada a 1 participantes de la quiniela 1
```

## 🧪 Testing con Postman

### 1. **Importar Colección**
- Abrir Postman
- Importar archivo: `QUINIELAS_API_POSTMAN_COLLECTION.json`
- Configurar variable `base_url` como `http://localhost:8000`

### 2. **Variables de Entorno**
```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "refresh_token": ""
}
```

### 3. **Flujo de Testing**
1. **Register** → Crear usuario
2. **Login** → Obtener tokens (se guardan automáticamente)
3. **Test Auth** → Verificar autenticación
4. **FCM Tokens** → Registrar token FCM
5. **Crear Quiniela** → Ver notificación automática
6. **Unirse Quiniela** → Ver notificación al creador
7. **Agregar Partido** → Crear partido
8. **Ingresar Resultado** → Ver notificación a participantes
9. **Test Notification** → Enviar notificación de prueba

## 🚨 Solución de Problemas

### 1. **Error de CORS**
```bash
# Verificar que django-cors-headers esté instalado
pip install django-cors-headers

# Verificar configuración en settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### 2. **Error de Firebase**
```bash
# Verificar que firebase-admin esté instalado
pip install firebase-admin==6.4.0

# Verificar configuración de Firebase
# Si no está configurado, funcionará en modo prueba
```

### 3. **Error de Base de Datos**
```bash
# Verificar migraciones
python manage.py showmigrations

# Aplicar migraciones pendientes
python manage.py migrate

# Verificar conexión
python manage.py dbshell
```

## 📱 Testing del Frontend Flutter

### 1. **Ejecutar App**
```bash
cd quiniela-front-v4
flutter run
```

### 2. **Verificar Logs**
- Los tokens FCM se envían automáticamente al servidor
- Las notificaciones se reciben en tiempo real
- Verificar logs en la consola de Flutter

### 3. **Testing de Notificaciones**
- Crear quiniela desde la app
- Unirse a quiniela
- Verificar que se reciban notificaciones push

## ✅ Checklist de Testing

- [ ] **Backend ejecutándose** en localhost:8000
- [ ] **Usuario registrado** y autenticado
- [ ] **Token FCM registrado** en el servidor
- [ ] **Quiniela creada** con notificación automática
- [ ] **Partido agregado** a la quiniela
- [ ] **Resultado ingresado** con notificación a participantes
- [ ] **Notificación de prueba** enviada exitosamente
- [ ] **Frontend Flutter** recibiendo notificaciones
- [ ] **Logs del servidor** mostrando actividad FCM

## 🎯 Resultado Esperado

Al completar todos los tests, deberías ver:
- ✅ Notificaciones automáticas funcionando
- ✅ Tokens FCM registrados correctamente
- ✅ Sistema de notificaciones robusto
- ✅ Frontend y backend 100% compatibles
- ✅ Logs detallados de todas las operaciones

**¡El sistema está listo para producción!** 🚀

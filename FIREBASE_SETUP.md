# Configuración de Firebase Cloud Messaging para Quinielas Backend

Este documento explica cómo configurar Firebase Cloud Messaging (FCM) para enviar notificaciones push desde tu aplicación Django.

## 🚀 Características Implementadas

- ✅ Modelo `FCMToken` para almacenar tokens de dispositivos
- ✅ Endpoint `/api/fcm-tokens/` para registrar/actualizar tokens
- ✅ Servicio `FCMService` para enviar notificaciones
- ✅ Notificaciones automáticas al cargar resultados de partidos
- ✅ Endpoint de prueba `/api/test-notification/`
- ✅ Configuración flexible de Firebase

## 📋 Prerrequisitos

1. **Cuenta de Google Firebase**
2. **Proyecto Firebase creado**
3. **Dependencias instaladas** (ya incluidas en requirements.txt)

## 🔧 Configuración de Firebase

### Paso 1: Crear Proyecto Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Haz clic en "Crear un proyecto"
3. Dale un nombre a tu proyecto (ej: "quinielas-app")
4. Sigue los pasos del asistente

### Paso 2: Obtener Credenciales

1. En tu proyecto Firebase, ve a **Project Settings** (⚙️)
2. Ve a la pestaña **Service Accounts**
3. Haz clic en **"Generate New Private Key"**
4. Descarga el archivo JSON
5. **IMPORTANTE**: Nunca subas este archivo a Git

### Paso 3: Configurar Credenciales

#### Opción A: Archivo de Credenciales (Recomendado para Producción)

1. Coloca el archivo JSON descargado en el directorio `quinielas_backend/`
2. Renómbralo como `firebase-credentials.json`
3. Agrega la variable de entorno:

```bash
# En tu archivo .env o variables de entorno
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

#### Opción B: Variables de Entorno (Para Desarrollo)

```bash
# En tu archivo .env
FIREBASE_CONFIG={"type": "service_account", "project_id": "tu-proyecto", ...}
```

## 📱 Endpoints de la API

### 1. Registrar Token FCM

```http
POST /api/fcm-tokens/
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "token": "fcm_token_del_dispositivo",
    "dispositivo": "iPhone 12",
    "plataforma": "ios"
}
```

### 2. Obtener Tokens del Usuario

```http
GET /api/fcm-tokens/
Authorization: Bearer <jwt_token>
```

### 3. Actualizar Token

```http
PUT /api/fcm-tokens/<token_id>/
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "dispositivo": "iPhone 12 Pro",
    "plataforma": "ios"
}
```

### 4. Desactivar Token

```http
DELETE /api/fcm-tokens/<token_id>/
Authorization: Bearer <jwt_token>
```

### 5. Probar Notificación

```http
POST /api/test-notification/
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "title": "Título de Prueba",
    "body": "Mensaje de prueba"
}
```

## 🔔 Notificaciones Automáticas

### Al Cargar Resultados de Partidos

Cuando se carga el resultado de un partido, automáticamente se envía una notificación a todos los participantes de la quiniela con:

- **Título**: "¡Resultado del partido!"
- **Cuerpo**: "DAL vs GB: Ganó GB"
- **Datos adicionales**: ID de quiniela, partido, ganador, etc.

### Datos de la Notificación

```json
{
    "tipo": "resultado_partido",
    "quiniela_id": "1",
    "partido_id": "5",
    "ganador_id": "8",
    "ganador_nombre": "Green Bay Packers",
    "ganador_abreviatura": "GB",
    "equipo_local": "DAL",
    "equipo_visitante": "GB"
}
```

## 🛠️ Desarrollo Local

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Firebase

```bash
# Copia tu archivo de credenciales
cp tu-archivo-credenciales.json quinielas_backend/firebase-credentials.json

# O configura variables de entorno
export FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

### 3. Ejecutar Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Probar

```bash
python manage.py runserver
```

## 🚀 Producción (Render)

### Variables de Entorno en Render

1. Ve a tu dashboard de Render
2. Selecciona tu servicio
3. Ve a **Environment**
4. Agrega:

```
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

### Subir Credenciales

1. Coloca `firebase-credentials.json` en tu repositorio
2. **IMPORTANTE**: Agrega este archivo a `.gitignore`
3. En Render, configura la ruta correcta

## 🔍 Troubleshooting

### Error: "Firebase no configurado"

- Verifica que las credenciales estén configuradas
- Revisa la ruta del archivo de credenciales
- Verifica las variables de entorno

### Error: "No hay tokens FCM activos"

- Los usuarios deben registrar sus tokens primero
- Verifica que los tokens estén marcados como `activo=True`

### Error: "Error al inicializar Firebase"

- Verifica el formato del archivo JSON
- Asegúrate de que el proyecto Firebase esté activo
- Revisa los permisos de la cuenta de servicio

## 📚 Recursos Adicionales

- [Firebase Admin SDK Python](https://firebase.google.com/docs/admin/setup#python)
- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
- [Django REST Framework](https://www.django-rest-framework.org/)

## 🤝 Contribución

Si encuentras algún problema o tienes sugerencias, por favor:

1. Revisa los logs de Django
2. Verifica la configuración de Firebase
3. Prueba con el endpoint de test
4. Abre un issue en el repositorio

---

**Nota**: Este sistema de notificaciones está diseñado para ser robusto y no fallar si Firebase no está configurado. Las notificaciones simplemente no se enviarán, pero la funcionalidad principal de la aplicación seguirá funcionando.

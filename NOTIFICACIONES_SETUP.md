# 🚀 Sistema de Notificaciones Push - Quinielas API

## 📱 Características Implementadas

### ✅ **Notificaciones Automáticas**
- **Nueva Quiniela**: Se envía a todos los usuarios cuando se crea una quiniela
- **Nuevo Participante**: Se notifica al creador cuando alguien se une
- **Resultados de Partidos**: Se notifica a todos los participantes cuando se ingresa un resultado
- **Elecciones Realizadas**: Se notifica al creador cuando un participante hace sus elecciones
- **Fecha Límite Próxima**: Notificaciones automáticas para quinielas próximas a vencer

### 🔧 **Endpoints de Notificaciones**
- `POST /api/fcm-tokens/` - Registrar token FCM de dispositivo
- `GET /api/fcm-tokens/` - Listar tokens del usuario
- `PUT /api/fcm-tokens/<id>/` - Actualizar token
- `DELETE /api/fcm-tokens/<id>/` - Desactivar token
- `POST /api/test-notification/` - Enviar notificación de prueba
- `POST /api/notifications/fecha-limite/` - Notificaciones de fecha límite (solo staff)

## 🚀 Configuración del Backend

### 1. **Instalar Dependencias**
```bash
pip install firebase-admin==6.4.0
```

### 2. **Configurar Firebase**
#### Opción A: Archivo de Credenciales (Recomendado para Producción)
1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto
3. Ve a Project Settings > Service Accounts
4. Haz clic en "Generate New Private Key"
5. Descarga el archivo JSON
6. Colócalo en el directorio del proyecto como `firebase-credentials.json`

#### Opción B: Variables de Entorno (Para Desarrollo)
```bash
export FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
# O
export FIREBASE_CONFIG='{"type": "service_account", "project_id": "tu-proyecto", ...}'
```

### 3. **Variables de Entorno**
```bash
# Firebase
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
# O
FIREBASE_CONFIG={"type": "service_account", "project_id": "tu-proyecto", ...}

# Logging
LOG_LEVEL=INFO
```

## 📱 Configuración del Frontend Flutter

### 1. **Dependencias en pubspec.yaml**
```yaml
dependencies:
  firebase_core: ^4.0.0
  firebase_messaging: ^16.0.0
  flutter_local_notifications: ^19.4.0
```

### 2. **Inicialización Automática**
El token FCM se envía automáticamente al servidor cuando:
- La app se inicia
- El usuario hace login
- Se obtiene un nuevo token FCM

### 3. **Manejo de Notificaciones**
```dart
// El servicio maneja automáticamente:
// - Notificaciones en primer plano
// - Notificaciones en segundo plano
// - Navegación al tocar notificaciones
// - Suscripción a temas de quinielas
```

## 🔄 Flujo de Notificaciones

### 1. **Registro de Token**
```
App Flutter → Obtiene Token FCM → Envía a /api/fcm-tokens/ → Backend almacena
```

### 2. **Envío de Notificaciones**
```
Backend → FCMService → Firebase → Dispositivos de Usuarios
```

### 3. **Tipos de Notificaciones**
- **Broadcast**: A todos los usuarios (nuevas quinielas)
- **Usuario Específico**: A un usuario en particular
- **Participantes de Quiniela**: A todos los participantes de una quiniela

## 🧪 Testing

### 1. **Notificación de Prueba**
```bash
POST /api/test-notification/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Notificación de Prueba",
  "body": "Esta es una notificación de prueba"
}
```

### 2. **Verificar Tokens FCM**
```bash
GET /api/fcm-tokens/
Authorization: Bearer <token>
```

### 3. **Notificaciones de Fecha Límite**
```bash
POST /api/notifications/fecha-limite/
Authorization: Bearer <token>
# Solo usuarios staff
```

## 📊 Logs y Monitoreo

### 1. **Logs del Backend**
- Todas las notificaciones se registran en los logs
- Errores de envío se capturan y registran
- Modo prueba disponible si Firebase no está configurado

### 2. **Métricas de Envío**
- Contador de notificaciones exitosas
- Contador de tokens activos
- Estadísticas por quiniela

## 🚨 Solución de Problemas

### 1. **Firebase No Configurado**
- El sistema funciona en "modo prueba"
- Las notificaciones se simulan en los logs
- No se envían realmente a los dispositivos

### 2. **Tokens Inválidos**
- Los tokens se marcan como inactivos automáticamente
- Se pueden reactivar enviando el mismo token nuevamente
- Limpieza automática de tokens obsoletos

### 3. **Errores de Envío**
- Reintentos automáticos en caso de fallo
- Logs detallados para debugging
- Fallback a modo simulación

## 🔮 Próximas Mejoras

- [ ] Notificaciones programadas
- [ ] Plantillas de notificaciones
- [ ] Analytics de engagement
- [ ] A/B testing de mensajes
- [ ] Integración con webhooks
- [ ] Dashboard de notificaciones

## 📞 Soporte

Para problemas o preguntas sobre el sistema de notificaciones:
1. Revisa los logs del backend
2. Verifica la configuración de Firebase
3. Prueba con el endpoint de test
4. Consulta la documentación de Firebase Admin SDK

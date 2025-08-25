# Ejemplos de Uso de la API de FCM

Este archivo contiene ejemplos prácticos de cómo usar los endpoints de Firebase Cloud Messaging.

## 🔐 Autenticación

Todos los endpoints requieren autenticación JWT. Primero obtén un token:

```bash
# 1. Registrar usuario
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario_prueba",
    "email": "usuario@ejemplo.com",
    "password": "password123"
  }'

# 2. Obtener token JWT
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario_prueba",
    "password": "password123"
  }'
```

## 📱 Gestión de Tokens FCM

### Registrar Token FCM

```bash
# Registrar token de dispositivo
curl -X POST http://localhost:8000/api/fcm-tokens/ \
  -H "Authorization: Bearer TU_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "fcm_token_del_dispositivo_aqui",
    "dispositivo": "iPhone 12",
    "plataforma": "ios"
  }'
```

**Respuesta exitosa:**
```json
{
  "mensaje": "Token FCM registrado exitosamente",
  "token_id": 1
}
```

### Obtener Tokens del Usuario

```bash
curl -X GET http://localhost:8000/api/fcm-tokens/ \
  -H "Authorization: Bearer TU_JWT_TOKEN"
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "token": "fcm_token_del_dispositivo_aqui",
    "dispositivo": "iPhone 12",
    "plataforma": "ios",
    "activo": true,
    "fecha_creacion": "2025-08-24T13:17:17.836Z",
    "ultima_actividad": "2025-08-24T13:17:17.836Z"
  }
]
```

### Actualizar Token

```bash
curl -X PUT http://localhost:8000/api/fcm-tokens/1/ \
  -H "Authorization: Bearer TU_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dispositivo": "iPhone 12 Pro",
    "plataforma": "ios"
  }'
```

### Desactivar Token

```bash
curl -X DELETE http://localhost:8000/api/fcm-tokens/1/ \
  -H "Authorization: Bearer TU_JWT_TOKEN"
```

## 🧪 Probar Notificaciones

### Enviar Notificación de Prueba

```bash
curl -X POST http://localhost:8000/api/test-notification/ \
  -H "Authorization: Bearer TU_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "¡Hola desde la API!",
    "body": "Esta es una notificación de prueba"
  }'
```

**Respuesta exitosa:**
```json
{
  "mensaje": "Notificación de prueba enviada exitosamente",
  "usuario": "usuario_prueba"
}
```

## 🔔 Notificaciones Automáticas

### Al Cargar Resultados de Partidos

Cuando cargas el resultado de un partido, automáticamente se envían notificaciones:

```bash
# Cargar resultado de partido
curl -X POST http://localhost:8000/api/quinielas/1/partidos/1/resultado/ \
  -H "Authorization: Bearer TU_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "resultado_equipo_id": 8
  }'
```

**Notificación automática enviada:**
- **Título**: "¡Resultado del partido!"
- **Cuerpo**: "DAL vs GB: Ganó GB"
- **Datos**: Información del partido, quiniela y ganador

## 📱 Ejemplos para Aplicaciones Móviles

### React Native / Expo

```javascript
import * as Notifications from 'expo-notifications';

// Solicitar permisos
const requestPermissions = async () => {
  const { status } = await Notifications.requestPermissionsAsync();
  return status === 'granted';
};

// Obtener token FCM
const getFCMToken = async () => {
  const token = await Notifications.getExpoPushTokenAsync({
    projectId: 'tu-proyecto-expo'
  });
  return token.data;
};

// Registrar token en el backend
const registerFCMToken = async (token) => {
  const response = await fetch('https://tu-api.com/api/fcm-tokens/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${jwtToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      token: token,
      dispositivo: 'iPhone 12',
      plataforma: 'ios'
    })
  });
  return response.json();
};
```

### Flutter

```dart
import 'package:firebase_messaging/firebase_messaging.dart';

class FCMService {
  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  
  Future<void> initialize() async {
    // Solicitar permisos
    NotificationSettings settings = await _firebaseMessaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );
    
    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      // Obtener token
      String? token = await _firebaseMessaging.getToken();
      if (token != null) {
        await registerToken(token);
      }
    }
  }
  
  Future<void> registerToken(String token) async {
    // Registrar en tu backend
    final response = await http.post(
      Uri.parse('https://tu-api.com/api/fcm-tokens/'),
      headers: {
        'Authorization': 'Bearer $jwtToken',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'token': token,
        'dispositivo': 'Android Device',
        'plataforma': 'android',
      }),
    );
  }
}
```

### JavaScript (Web)

```javascript
// Solicitar permisos de notificación
const requestNotificationPermission = async () => {
  if ('Notification' in window) {
    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }
  return false;
};

// Obtener token FCM (requiere Firebase SDK)
const getFCMToken = async () => {
  const messaging = firebase.messaging();
  const token = await messaging.getToken();
  return token;
};

// Registrar token en el backend
const registerFCMToken = async (token) => {
  const response = await fetch('/api/fcm-tokens/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${jwtToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      token: token,
      dispositivo: 'Chrome Browser',
      plataforma: 'web',
    }),
  });
  return response.json();
};
```

## 🔍 Debugging y Troubleshooting

### Verificar Tokens Registrados

```bash
# Ver tokens en la base de datos
curl -X GET http://localhost:8000/api/fcm-tokens/ \
  -H "Authorization: Bearer TU_JWT_TOKEN"
```

### Verificar Logs

```bash
# Ver logs de Django
tail -f quinielas_backend/logs/django.log

# Ver logs específicos de FCM
grep "FCM\|Firebase" quinielas_backend/logs/django.log
```

### Probar Notificación Manual

```bash
# Enviar notificación de prueba
curl -X POST http://localhost:8000/api/test-notification/ \
  -H "Authorization: Bearer TU_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test",
    "body": "Testing FCM"
  }'
```

## 📊 Monitoreo

### Estadísticas de Tokens

```bash
# Ver todos los tokens (solo admin)
python manage.py shell

>>> from api.models import FCMToken
>>> FCMToken.objects.count()  # Total de tokens
>>> FCMToken.objects.filter(activo=True).count()  # Tokens activos
>>> FCMToken.objects.filter(plataforma='ios').count()  # Tokens iOS
>>> FCMToken.objects.filter(plataforma='android').count()  # Tokens Android
```

### Verificar Estado de Firebase

```bash
# Ejecutar script de prueba
python test_firebase.py
```

---

## 🚀 Próximos Pasos

1. **Configura Firebase** siguiendo `FIREBASE_SETUP.md`
2. **Prueba los endpoints** con los ejemplos de arriba
3. **Integra en tu app móvil** usando los ejemplos proporcionados
4. **Monitorea las notificaciones** en Firebase Console
5. **Personaliza las notificaciones** según tus necesidades

¡Las notificaciones push están listas para usar! 🎉

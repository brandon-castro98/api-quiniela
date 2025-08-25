# 🏈 Quinielas Backend API

Backend de Django REST Framework para la aplicación de quinielas de la NFL con notificaciones push integradas.

## 🚀 Características

- **API REST completa** para gestión de quinielas, partidos y usuarios
- **Autenticación JWT** segura y robusta
- **Notificaciones push** con Firebase Cloud Messaging
- **Sistema de permisos** granular
- **Base de datos optimizada** con relaciones eficientes
- **Documentación completa** de endpoints

## 🛠️ Tecnologías

- **Django 5.0.6** - Framework web
- **Django REST Framework** - API REST
- **Firebase Admin SDK** - Notificaciones push
- **JWT** - Autenticación
- **PostgreSQL/SQLite** - Base de datos
- **Gunicorn** - Servidor WSGI

## 📋 Prerrequisitos

- Python 3.8+
- pip
- Virtual environment (recomendado)

## 🔧 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/brandon-castro98/api-quiniela.git
cd api-quiniela
```

### 2. Crear entorno virtual
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
# o
env\Scripts\activate     # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp env.example .env
# Editar .env con tus configuraciones
```

### 5. Ejecutar migraciones
```bash
python manage.py migrate
```

### 6. Crear superusuario
```bash
python manage.py createsuperuser
```

### 7. Ejecutar servidor
```bash
python manage.py runserver
```

## 🔥 Configuración de Firebase

### 1. Crear proyecto en Firebase Console
- Ve a [Firebase Console](https://console.firebase.google.com/)
- Crea un nuevo proyecto
- Habilita Cloud Messaging

### 2. Obtener credenciales
- Ve a Project Settings > Service Accounts
- Haz clic en "Generate New Private Key"
- Descarga el archivo JSON

### 3. Configurar en Django
```bash
# Opción 1: Archivo de credenciales
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Opción 2: Variables de entorno
FIREBASE_CONFIG={"type": "service_account", ...}
```

## 📱 Endpoints Principales

### Autenticación
- `POST /api/register/` - Registrar usuario
- `POST /api/login/` - Iniciar sesión
- `POST /api/token/refresh/` - Refrescar token

### Quinielas
- `GET/POST /api/quinielas/` - Listar/crear quinielas
- `GET/DELETE /api/quinielas/<id>/` - Ver/eliminar quiniela
- `POST /api/quinielas/<id>/unirse/` - Unirse a quiniela

### Partidos
- `GET/POST /api/quinielas/<id>/partidos/` - Partidos de quiniela
- `POST /api/quinielas/<id>/partidos/<id>/resultado/` - Cargar resultado

### FCM (Notificaciones)
- `POST /api/fcm-tokens/` - Registrar token FCM
- `GET /api/fcm-tokens/` - Obtener tokens del usuario
- `POST /api/test-notification/` - Probar notificación

## 🧪 Testing

### Ejecutar tests
```bash
python manage.py test
```

### Verificar configuración
```bash
python test_firebase.py
```

## 🚀 Despliegue

### Render
1. Conectar repositorio a Render
2. Configurar variables de entorno
3. Deploy automático

### Variables de entorno requeridas
```bash
SECRET_KEY=tu-secret-key
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

## 📊 Estructura del Proyecto

```
quinielas_backend/
├── api/                    # Aplicación principal
│   ├── models.py          # Modelos de datos
│   ├── views.py           # Vistas de la API
│   ├── serializer.py      # Serializers
│   ├── services.py        # Servicios (FCM)
│   └── urls.py            # URLs de la API
├── quinielas_backend/      # Configuración del proyecto
│   ├── settings.py        # Configuración Django
│   └── urls.py            # URLs principales
├── requirements.txt        # Dependencias
├── manage.py              # Comandos Django
└── README.md              # Este archivo
```

## 🔍 Troubleshooting

### Error: "Firebase no configurado"
- Verifica que las credenciales estén configuradas
- Revisa la ruta del archivo de credenciales
- Verifica las variables de entorno

### Error: "No hay tokens FCM activos"
- Los usuarios deben registrar sus tokens primero
- Verifica que los tokens estén marcados como `activo=True`

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

- **Documentación**: Ver archivos en `docs/`
- **Contacto Directo**: jonathan_works98@outlook.com

---

**¡Disfruta creando quinielas! 🏈✨**

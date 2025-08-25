# 🔥 CONFIGURACIÓN DE FIREBASE PARA NOTIFICACIONES PUSH

## 📋 **PASOS PARA CONFIGURAR FIREBASE**

### **1. Crear Proyecto en Firebase Console**
1. **Ve a** [Firebase Console](https://console.firebase.google.com/)
2. **Inicia sesión** con tu cuenta de Google
3. **Crea nuevo proyecto**:
   - Nombre: `quiniela-notifications` (o el que prefieras)
   - Habilita Google Analytics: Opcional
   - Crear proyecto

### **2. Habilitar Cloud Messaging (FCM)**
1. **En tu proyecto** → **Cloud Messaging**
2. **Verifica** que esté habilitado
3. **Anota** el Project ID (lo necesitarás después)

### **3. Obtener Credenciales de Servicio**
1. **Configuración** (⚙️) → **Configuración del proyecto**
2. **Pestaña "Cuentas de servicio"**
3. **Sección "Firebase Admin SDK"**
4. **Hacer clic** en "Generar nueva clave privada"
5. **Descargar** el archivo JSON
6. **Guardar** como `firebase-credentials.json` en este directorio

### **4. Configurar Variables de Entorno**

#### **Opción A: Archivo JSON (Recomendado para desarrollo)**
```bash
# En tu archivo .env local
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

#### **Opción B: Variables individuales (Para Render)**
```bash
# En tu dashboard de Render, agrega estas variables:

FIREBASE_PROJECT_ID=tu-proyecto-id
FIREBASE_PRIVATE_KEY_ID=tu-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nTU_CLAVE_PRIVADA_AQUI\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@tu-proyecto.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=tu-client-id
```

### **5. Estructura del Archivo JSON de Credenciales**
El archivo `firebase-credentials.json` debe tener esta estructura:
```json
{
  "type": "service_account",
  "project_id": "tu-proyecto-quiniela",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@tu-proyecto-quiniela.iam.gserviceaccount.com",
  "client_id": "123456789...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40tu-proyecto-quiniela.iam.gserviceaccount.com"
}
```

## 🧪 **PROBAR CONFIGURACIÓN**

### **1. Localmente**
```bash
# Probar configuración
python firebase_config.py

# Resultado esperado:
✅ Usando archivo de credenciales: ./firebase-credentials.json
✅ Firebase inicializado correctamente
✅ Conexión con Firebase exitosa
🔔 Notificaciones push funcionando
```

### **2. En Render**
```bash
# Verificar variables de entorno
python manage.py shell -c "from firebase_config import test_firebase_connection; test_firebase_connection()"
```

## 🚀 **DESPLIEGUE EN RENDER**

### **1. Subir Credenciales**
```bash
# Opción A: Archivo JSON
git add firebase-credentials.json
git commit -m "🔑 Agregadas credenciales Firebase"
git push origin Evolution-library-teams

# Opción B: Solo variables de entorno
# No subir archivo JSON, solo configurar en Render
```

### **2. Configurar Variables en Render**
1. **Dashboard de Render** → **Tu servicio**
2. **Environment** → **Environment Variables**
3. **Agregar** todas las variables de Firebase
4. **Redeploy** automático

### **3. Verificar Funcionamiento**
```bash
# En Render, probar:
python manage.py shell -c "from firebase_config import test_firebase_connection; test_firebase_connection()"
```

## 🔒 **SEGURIDAD**

### **⚠️ IMPORTANTE:**
- **NUNCA** subas credenciales reales a GitHub
- **Usa** `.gitignore` para excluir archivos de credenciales
- **En producción** usa variables de entorno
- **En desarrollo** puedes usar archivo JSON local

### **Archivos a excluir en .gitignore:**
```gitignore
# Firebase
firebase-credentials.json
.env
.env.local
.env.production
```

## 🎯 **RESULTADO FINAL**

Una vez configurado correctamente:
- ✅ **Notificaciones push** funcionarán en tiempo real
- ✅ **Frontend** recibirá notificaciones
- ✅ **Backend** enviará notificaciones automáticamente
- ✅ **Usuarios** recibirán alertas en sus dispositivos

## 🆘 **SOLUCIÓN DE PROBLEMAS**

### **Error: "No se pudieron obtener credenciales"**
- Verifica que el archivo JSON esté en el directorio correcto
- Verifica que las variables de entorno estén configuradas
- Verifica que el archivo JSON tenga el formato correcto

### **Error: "firebase-admin no está instalado"**
```bash
pip install firebase-admin
```

### **Error: "Credenciales inválidas"**
- Verifica que el archivo JSON sea el correcto
- Verifica que las variables de entorno tengan los valores correctos
- Verifica que el proyecto de Firebase esté activo

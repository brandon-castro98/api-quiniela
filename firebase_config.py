"""
Configuración de Firebase para Django

Este archivo contiene la configuración necesaria para Firebase Cloud Messaging.
Para usar este archivo:

1. Ve a https://console.firebase.google.com/
2. Crea un nuevo proyecto o selecciona uno existente
3. Ve a Project Settings > Service Accounts
4. Haz clic en "Generate New Private Key"
5. Descarga el archivo JSON
6. Coloca el archivo en este directorio y renómbralo como 'firebase-credentials.json'
7. O configura las variables de entorno como se muestra abajo

Variables de entorno necesarias:
- FIREBASE_CREDENTIALS_PATH: Ruta al archivo de credenciales JSON
- FIREBASE_PROJECT_ID: ID del proyecto de Firebase
- FIREBASE_PRIVATE_KEY: Clave privada (con \n para saltos de línea)
- FIREBASE_CLIENT_EMAIL: Email del cliente de servicio
- FIREBASE_CLIENT_ID: ID del cliente
- FIREBASE_PRIVATE_KEY_ID: ID de la clave privada

Ejemplo de .env:
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_PROJECT_ID=tu-proyecto-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nTU_PRIVATE_KEY_AQUI\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@tu-proyecto.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=tu-client-id
FIREBASE_PRIVATE_KEY_ID=tu-private-key-id
"""

import os
import json
from decouple import config

def get_firebase_credentials():
    """
    Obtiene las credenciales de Firebase desde variables de entorno o archivo
    """
    try:
        # Opción 1: Archivo JSON de credenciales
        credentials_path = config('FIREBASE_CREDENTIALS_PATH', default=None)
        
        # Si no hay variable de entorno, buscar en el directorio actual
        if not credentials_path:
            credentials_path = "./firebase-credentials.json"
        
        if os.path.exists(credentials_path):
            print(f"✅ Usando archivo de credenciales: {credentials_path}")
            return credentials_path
        
        # Opción 2: Variables de entorno
        project_id = config('FIREBASE_PROJECT_ID', default=None)
        private_key = config('FIREBASE_PRIVATE_KEY', default=None)
        client_email = config('FIREBASE_CLIENT_EMAIL', default=None)
        
        if all([project_id, private_key, client_email]):
            print("✅ Usando credenciales desde variables de entorno")
            return {
                "type": "service_account",
                "project_id": project_id,
                "private_key_id": config('FIREBASE_PRIVATE_KEY_ID', default=""),
                "private_key": private_key.replace('\\n', '\n'),
                "client_email": client_email,
                "client_id": config('FIREBASE_CLIENT_ID', default=""),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email}"
            }
        
        # Opción 3: Configuración por defecto (solo para desarrollo)
        print("⚠️  No se encontraron credenciales de Firebase")
        print("🔧 Usando configuración de desarrollo")
        return None
        
    except Exception as e:
        print(f"❌ Error obteniendo credenciales de Firebase: {e}")
        return None

def initialize_firebase():
    """
    Inicializa Firebase Admin SDK
    """
    try:
        import firebase_admin
        from firebase_admin import credentials
        
        # Verificar si ya está inicializado
        if firebase_admin._apps:
            print("✅ Firebase ya está inicializado")
            return True
        
        # Obtener credenciales
        firebase_creds = get_firebase_credentials()
        
        if not firebase_creds:
            print("❌ No se pudieron obtener credenciales de Firebase")
            return False
        
        # Inicializar Firebase
        if isinstance(firebase_creds, str):
            # Es un archivo JSON
            cred = credentials.Certificate(firebase_creds)
        else:
            # Es un diccionario
            cred = credentials.Certificate(firebase_creds)
        
        firebase_admin.initialize_app(cred)
        print("✅ Firebase inicializado correctamente")
        return True
        
    except ImportError:
        print("❌ firebase-admin no está instalado")
        print("💡 Instala con: pip install firebase-admin")
        return False
    except Exception as e:
        print(f"❌ Error inicializando Firebase: {e}")
        return False

def test_firebase_connection():
    """
    Prueba la conexión con Firebase
    """
    try:
        if initialize_firebase():
            import firebase_admin
            from firebase_admin import messaging
            
            # Intentar enviar un mensaje de prueba
            message = messaging.Message(
                notification=messaging.Notification(
                    title="Prueba de Conexión",
                    body="Firebase está funcionando correctamente"
                ),
                topic="test"
            )
            
            print("✅ Conexión con Firebase exitosa")
            print("🔔 Notificaciones push funcionando")
            return True
        else:
            print("❌ No se pudo conectar con Firebase")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de conexión: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Probando configuración de Firebase...")
    test_firebase_connection()

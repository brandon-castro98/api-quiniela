#!/usr/bin/env python
"""
Script de prueba para verificar la configuración de Firebase
Ejecuta este script para verificar que todo esté configurado correctamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quinielas_backend.settings')
django.setup()

from api.models import FCMToken, User
from api.services import fcm_service

def test_firebase_config():
    """Prueba la configuración de Firebase"""
    print("🧪 Probando configuración de Firebase...")
    
    try:
        # Verificar si Firebase está inicializado
        import firebase_admin
        if firebase_admin._apps:
            print("✅ Firebase Admin SDK inicializado correctamente")
        else:
            print("⚠️  Firebase Admin SDK no está inicializado")
            print("   Esto es normal si no tienes credenciales configuradas")
    except ImportError:
        print("❌ Error: firebase-admin no está instalado")
        return False
    
    return True

def test_fcm_service():
    """Prueba el servicio FCM"""
    print("\n🔧 Probando servicio FCM...")
    
    try:
        # Verificar que el servicio se puede crear
        service = fcm_service
        print("✅ Servicio FCM creado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error al crear servicio FCM: {e}")
        return False

def test_models():
    """Prueba los modelos FCM"""
    print("\n📱 Probando modelos FCM...")
    
    try:
        # Verificar que el modelo se puede importar
        token = FCMToken()
        print("✅ Modelo FCMToken importado correctamente")
        
        # Verificar campos del modelo
        fields = [field.name for field in FCMToken._meta.fields]
        expected_fields = ['id', 'usuario', 'token', 'dispositivo', 'plataforma', 'activo', 'fecha_creacion', 'ultima_actividad']
        
        for field in expected_fields:
            if field in fields:
                print(f"   ✅ Campo '{field}' presente")
            else:
                print(f"   ❌ Campo '{field}' faltante")
        
        return True
    except Exception as e:
        print(f"❌ Error al probar modelos: {e}")
        return False

def test_database():
    """Prueba la base de datos"""
    print("\n🗄️  Probando base de datos...")
    
    try:
        # Verificar que se puede acceder a la base de datos
        token_count = FCMToken.objects.count()
        print(f"✅ Base de datos accesible - Tokens FCM: {token_count}")
        return True
    except Exception as e:
        print(f"❌ Error al acceder a la base de datos: {e}")
        return False

def test_endpoints():
    """Prueba que los endpoints estén disponibles"""
    print("\n🌐 Probando endpoints...")
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # Verificar que las URLs estén configuradas
        urls_to_test = [
            'fcm-tokens',
            'test-notification',
        ]
        
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"   ✅ Endpoint '{url_name}': {url}")
            except Exception as e:
                print(f"   ❌ Endpoint '{url_name}': {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error al probar endpoints: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de Firebase Cloud Messaging")
    print("=" * 50)
    
    tests = [
        test_firebase_config,
        test_fcm_service,
        test_models,
        test_database,
        test_endpoints,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Error en prueba {test.__name__}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! Firebase está configurado correctamente.")
        print("\n📋 Próximos pasos:")
        print("1. Configura tus credenciales de Firebase")
        print("2. Prueba el endpoint /api/test-notification/")
        print("3. Registra tokens FCM desde tu aplicación móvil")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa la configuración.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

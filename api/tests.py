from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Quiniela, Participante, Partido, Equipo, FCMToken

User = get_user_model()

class QuinielaModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.quiniela = Quiniela.objects.create(
            nombre='Quiniela de Prueba',
            apuesta_individual=10.00,
            creada_por=self.user
        )

    def test_quiniela_creation(self):
        self.assertEqual(self.quiniela.nombre, 'Quiniela de Prueba')
        self.assertEqual(self.quiniela.apuesta_individual, 10.00)
        self.assertEqual(self.quiniela.creada_por, self.user)
        self.assertFalse(self.quiniela.mostrar_elecciones)

class FCMTokenModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_fcm_token_creation(self):
        token = FCMToken.objects.create(
            usuario=self.user,
            token='test_fcm_token_123',
            dispositivo='iPhone Test',
            plataforma='ios'
        )
        
        self.assertEqual(token.usuario, self.user)
        self.assertEqual(token.token, 'test_fcm_token_123')
        self.assertEqual(token.dispositivo, 'iPhone Test')
        self.assertEqual(token.plataforma, 'ios')
        self.assertTrue(token.activo)

class QuinielaAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_quiniela(self):
        data = {
            'nombre': 'Quiniela API Test',
            'apuesta_individual': 15.00
        }
        
        response = self.client.post('/api/quinielas/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiniela.objects.count(), 1)
        self.assertEqual(Quiniela.objects.first().creada_por, self.user)

    def test_list_quinielas(self):
        # Crear quiniela específica para este test
        quiniela = Quiniela.objects.create(
            nombre='Quiniela Test List',
            apuesta_individual=20.00,
            creada_por=self.user
        )
        
        response = self.client.get('/api/quinielas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que la quiniela creada esté en la respuesta
        quiniela_names = [q['nombre'] for q in response.data['results']]
        self.assertIn('Quiniela Test List', quiniela_names)

class FCMTokenAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_register_fcm_token(self):
        data = {
            'token': 'test_fcm_token_123',
            'dispositivo': 'Android Test',
            'plataforma': 'android'
        }
        
        response = self.client.post('/api/fcm-tokens/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FCMToken.objects.count(), 1)
        
        token = FCMToken.objects.first()
        self.assertEqual(token.usuario, self.user)
        self.assertEqual(token.token, 'test_fcm_token_123')
        self.assertEqual(token.plataforma, 'android')

    def test_get_user_tokens(self):
        FCMToken.objects.create(
            usuario=self.user,
            token='test_token_1',
            plataforma='ios'
        )
        
        response = self.client.get('/api/fcm-tokens/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['token'], 'test_token_1')

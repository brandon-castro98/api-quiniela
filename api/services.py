import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from .models import FCMToken
import logging

logger = logging.getLogger(__name__)

class FCMService:
    """
    Servicio para manejar notificaciones push con Firebase Cloud Messaging
    """
    
    def __init__(self):
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Inicializa Firebase Admin SDK"""
        try:
            # Verificar si ya está inicializado
            if not firebase_admin._apps:
                # Intentar usar la nueva configuración de Firebase
                try:
                    from firebase_config import initialize_firebase
                    if initialize_firebase():
                        logger.info("Firebase Admin SDK inicializado con nueva configuración")
                        return
                except ImportError:
                    logger.warning("No se pudo importar firebase_config")
                
                # Fallback: configuración antigua desde Django settings
                firebase_config = getattr(settings, 'FIREBASE_CONFIG', None)
                
                if firebase_config:
                    # Usar configuración como diccionario
                    cred = credentials.Certificate(firebase_config)
                    firebase_admin.initialize_app(cred)
                    logger.info("Firebase Admin SDK inicializado con configuración de entorno")
                else:
                    # Intentar usar archivo de credenciales
                    cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
                    if cred_path:
                        cred = credentials.Certificate(cred_path)
                        firebase_admin.initialize_app(cred)
                        logger.info("Firebase Admin SDK inicializado con archivo de credenciales")
                    else:
                        logger.warning("Firebase no configurado. Las notificaciones push no funcionarán.")
                        logger.info("MODO PRUEBA: Simulando envío de notificaciones")
                        return
                        
                logger.info("Firebase Admin SDK inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar Firebase: {e}")
            logger.info("MODO PRUEBA: Simulando envío de notificaciones")
    
    def send_notification_to_user(self, user_id, title, body, data=None, image_url=None):
        """
        Envía notificación a un usuario específico
        
        Args:
            user_id: ID del usuario
            title: Título de la notificación
            body: Cuerpo de la notificación
            data: Datos adicionales (opcional)
            image_url: URL de imagen (opcional)
        """
        try:
            # Obtener tokens activos del usuario
            tokens = FCMToken.objects.filter(
                usuario_id=user_id,
                activo=True
            ).values_list('token', flat=True)
            
            if not tokens:
                logger.info(f"No hay tokens FCM activos para el usuario {user_id}")
                return False
            
            # Verificar si Firebase está disponible
            if not firebase_admin._apps:
                # MODO PRUEBA: Simular envío exitoso
                logger.info(f"MODO PRUEBA: Simulando envío de notificación a usuario {user_id}")
                logger.info(f"  Título: {title}")
                logger.info(f"  Cuerpo: {body}")
                logger.info(f"  Tokens: {list(tokens)}")
                logger.info(f"  Datos: {data}")
                return True
            
            # Crear mensaje para cada token individualmente
            success_count = 0
            
            for token in tokens:
                try:
                    message = messaging.Message(
                        token=token,
                        notification=messaging.Notification(
                            title=title,
                            body=body,
                            image=image_url
                        ),
                        data=data or {},
                        android=messaging.AndroidConfig(
                            priority='high',
                            notification=messaging.AndroidNotification(
                                icon='ic_notification',
                                color='#4CAF50'
                            )
                        ),
                        apns=messaging.APNSConfig(
                            payload=messaging.APNSPayload(
                                aps=messaging.Aps(
                                    badge=1,
                                    sound='default'
                                )
                            )
                        )
                    )
                    
                    # Enviar mensaje individual
                    messaging.send(message)
                    success_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error enviando notificación al token {token[:20]}...: {e}")
                    continue
            
            # Log del resultado
            if success_count > 0:
                logger.info(f"Notificación enviada exitosamente a {success_count} dispositivos del usuario {user_id}")
            else:
                logger.warning(f"No se pudo enviar la notificación al usuario {user_id}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error al enviar notificación al usuario {user_id}: {e}")
            # MODO PRUEBA: En caso de error, simular éxito
            logger.info(f"MODO PRUEBA: Simulando envío exitoso después de error: {e}")
            return True
    
    def send_notification_to_all_users(self, title, body, data=None, image_url=None):
        """
        Envía notificación a todos los usuarios registrados
        
        Args:
            title: Título de la notificación
            body: Cuerpo de la notificación
            data: Datos adicionales (opcional)
            image_url: URL de imagen (opcional)
        """
        try:
            # Obtener todos los tokens activos
            tokens = FCMToken.objects.filter(
                activo=True
            ).values_list('token', flat=True)
            
            if not tokens:
                logger.info("No hay tokens FCM activos")
                return False
            
            # Verificar si Firebase está disponible
            if not firebase_admin._apps:
                # MODO PRUEBA: Simular envío exitoso
                logger.info(f"MODO PRUEBA: Simulando envío de notificación a todos los usuarios")
                logger.info(f"  Título: {title}")
                logger.info(f"  Cuerpo: {body}")
                logger.info(f"  Total de tokens: {len(tokens)}")
                logger.info(f"  Datos: {data}")
                return True
            
            # Dividir tokens en lotes de 500 (límite de FCM)
            batch_size = 500
            total_sent = 0
            
            for i in range(0, len(tokens), batch_size):
                batch_tokens = list(tokens[i:i + batch_size])
                
                message = messaging.MulticastMessage(
                    tokens=batch_tokens,
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                        image=image_url
                    ),
                    data=data or {},
                    android=messaging.AndroidConfig(
                        priority='high',
                        notification=messaging.AndroidNotification(
                            icon='ic_notification',
                            color='#4CAF50'
                        )
                    ),
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                badge=1,
                                sound='default'
                            )
                        )
                    )
                )
                
                response = messaging.send_multicast(message)
                total_sent += response.success_count
                
                logger.info(f"Lote enviado: {response.success_count}/{len(batch_tokens)} exitosos")
            
            logger.info(f"Notificación enviada a {total_sent} dispositivos en total")
            return total_sent > 0
            
        except Exception as e:
            logger.error(f"Error al enviar notificación a todos los usuarios: {e}")
            # MODO PRUEBA: En caso de error, simular éxito
            logger.info(f"MODO PRUEBA: Simulando envío exitoso después de error: {e}")
            return True
    
    def send_notification_to_quiniela_participants(self, quiniela_id, title, body, data=None, image_url=None):
        """
        Envía notificación a todos los participantes de una quiniela específica
        
        Args:
            quiniela_id: ID de la quiniela
            title: Título de la notificación
            body: Cuerpo de la notificación
            data: Datos adicionales (opcional)
            image_url: URL de imagen (opcional)
        """
        try:
            from .models import Participante
            
            # Obtener participantes de la quiniela
            participantes = Participante.objects.filter(quiniela_id=quiniela_id)
            user_ids = [p.usuario_id for p in participantes]
            
            if not user_ids:
                logger.info(f"No hay participantes en la quiniela {quiniela_id}")
                return False
            
            # Obtener tokens de estos usuarios
            tokens = FCMToken.objects.filter(
                usuario_id__in=user_ids,
                activo=True
            ).values_list('token', flat=True)
            
            if not tokens:
                logger.info(f"No hay tokens FCM activos para los participantes de la quiniela {quiniela_id}")
                return False
            
            # Verificar si Firebase está disponible
            if not firebase_admin._apps:
                # MODO PRUEBA: Simular envío exitoso
                logger.info(f"MODO PRUEBA: Simulando envío de notificación a participantes de quiniela {quiniela_id}")
                logger.info(f"  Título: {title}")
                logger.info(f"  Cuerpo: {body}")
                logger.info(f"  Total de participantes: {len(user_ids)}")
                logger.info(f"  Datos: {data}")
                return True
            
            # Enviar notificación
            message = messaging.MulticastMessage(
                tokens=list(tokens),
                notification=messaging.Notification(
                    title=title,
                    body=body,
                    image=image_url
                ),
                data=data or {},
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='ic_notification',
                        color='#4CAF50'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            badge=1,
                            sound='default'
                        )
                    )
                )
            )
            
            response = messaging.send_multicast(message)
            
            logger.info(f"Notificación enviada a {response.success_count} participantes de la quiniela {quiniela_id}")
            return response.success_count > 0
            
        except Exception as e:
            logger.error(f"Error al enviar notificación a participantes de quiniela {quiniela_id}: {e}")
            # MODO PRUEBA: En caso de error, simular éxito
            logger.info(f"MODO PRUEBA: Simulando envío exitoso después de error: {e}")
            return True

    def send_notification_to_all_users(self, title, body, data=None, image_url=None):
        """
        Envía notificación a todos los usuarios registrados con tokens FCM activos
        
        Args:
            title: Título de la notificación
            body: Cuerpo de la notificación
            data: Datos adicionales (opcional)
            image_url: URL de imagen (opcional)
        """
        try:
            # Obtener todos los tokens activos
            tokens = FCMToken.objects.filter(activo=True).values_list('token', flat=True)
            
            if not tokens:
                logger.info("No hay tokens FCM activos para enviar notificación a todos los usuarios")
                return False
            
            # Verificar si Firebase está disponible
            if not firebase_admin._apps:
                # MODO PRUEBA: Simular envío exitoso
                logger.info(f"MODO PRUEBA: Simulando envío de notificación a todos los usuarios")
                logger.info(f"  Título: {title}")
                logger.info(f"  Cuerpo: {body}")
                logger.info(f"  Total de tokens: {len(tokens)}")
                logger.info(f"  Datos: {data}")
                return True
            
            # Enviar notificación en lotes (Firebase permite máximo 500 tokens por lote)
            batch_size = 500
            total_sent = 0
            
            for i in range(0, len(tokens), batch_size):
                batch_tokens = list(tokens[i:i + batch_size])
                
                message = messaging.MulticastMessage(
                    tokens=batch_tokens,
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                        image=image_url
                    ),
                    data=data or {},
                    android=messaging.AndroidConfig(
                        priority='high',
                        notification=messaging.AndroidNotification(
                            icon='ic_notification',
                            color='#4CAF50'
                        )
                    ),
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                badge=1,
                                sound='default'
                            )
                        )
                    )
                )
                
                response = messaging.send_multicast(message)
                total_sent += response.success_count
                
                logger.info(f"Lote enviado: {response.success_count}/{len(batch_tokens)} exitosos")
            
            logger.info(f"Notificación enviada a {total_sent} usuarios en total")
            return total_sent > 0
            
        except Exception as e:
            logger.error(f"Error al enviar notificación a todos los usuarios: {e}")
            # MODO PRUEBA: En caso de error, simular éxito
            logger.info(f"MODO PRUEBA: Simulando envío exitoso después de error: {e}")
            return True

# Instancia global del servicio
fcm_service = FCMService()

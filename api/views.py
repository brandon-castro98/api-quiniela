from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, viewsets, permissions
from django.utils import timezone
from .models import Quiniela, Participante, Partido, Eleccion, Equipo
from .serializer import (
    EquipoSerializer, UserRegisterSerializer, QuinielaSerializer, 
    ParticipanteSerializer, PartidoSerializer, EleccionCreateSerializer, 
    FechaLimiteSerializer, PartidoReadSerializer, PartidoWriteByIdSerializer
)
from .permissions import EsCreadorDeQuiniela
from .models import FCMToken
from .serializer import FCMTokenCreateSerializer, FCMTokenSerializer
import logging
from datetime import datetime
from .services import FCMService

logger = logging.getLogger(__name__)

# Instancia global del servicio FCM
fcm_service = FCMService()

# Create your views here.
class PartidoListCreateForQuinielaView(generics.ListCreateAPIView):
    """
    GET  /api/quinielas/<quiniela_id>/partidos/  -> lista partidos de esa quiniela
    POST /api/quinielas/<quiniela_id>/partidos/  -> crea partido en esa quiniela:
        Opción A (por IDs):
            { "equipo_local_id": 5, "equipo_visitante_id": 8, "fecha": "2025-09-05T19:00:00Z" }
        Opción B (por texto: nombre/abreviatura):
            { "equipo_local_abreviatura": "DAL", "equipo_visitante_abreviatura": "GB", "fecha": "..." }
            o con ..._nombre en vez de ..._abreviatura
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        quiniela_id = self.kwargs['quiniela_id']
        return Partido.objects.filter(quiniela_id=quiniela_id).order_by('fecha', 'id')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PartidoReadSerializer
        return PartidoWriteByIdSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        quiniela = get_object_or_404(Quiniela, pk=self.kwargs['quiniela_id'])
        if quiniela.creada_por != request.user and not request.user.is_staff:
            raise PermissionDenied("Solo el creador de la quiniela puede agregar partidos.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        local = get_object_or_404(Equipo, pk=serializer.validated_data['equipo_local_id'])
        visitante = get_object_or_404(Equipo, pk=serializer.validated_data['equipo_visitante_id'])
        fecha = serializer.validated_data['fecha']

        if local.id == visitante.id:
            raise ValidationError('El equipo local y visitante no pueden ser el mismo.')

        partido = Partido.objects.create(
            quiniela=quiniela,
            equipo_local=local,
            equipo_visitante=visitante,
            fecha=fecha
        )

        out = PartidoReadSerializer(partido).data
        return Response(out, status=201)


class PartidoResultadoView(generics.GenericAPIView):
    """
    POST /api/quinielas/<quiniela_id>/partidos/<partido_id>/resultado/
    Body (una de estas variantes):
      - { "resultado_equipo_id": 8 }
      - { "resultado_abreviatura": "GB" }
      - { "resultado_nombre": "Green Bay Packers" }
    Reglas:
      - Solo creador de la quiniela o staff puede cargar resultado
      - El ganador debe ser uno de los dos equipos del partido
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        quiniela_id = self.kwargs['quiniela_id']
        partido_id = self.kwargs['partido_id']

        partido = (Partido.objects
                   .select_related('quiniela', 'equipo_local', 'equipo_visitante')
                   .filter(id=partido_id, quiniela_id=quiniela_id)
                   .first())
        if not partido:
            raise NotFound("Partido no encontrado en esta quiniela.")

        # Permisos
        if partido.quiniela.creada_por != request.user and not request.user.is_staff:
            raise PermissionDenied("No tienes permisos para cargar el resultado de este partido.")

        data = request.data

        # Resolver ganador
        ganador = None
        if 'resultado_equipo_id' in data:
            try:
                ganador = Equipo.objects.get(pk=data['resultado_equipo_id'])
            except Equipo.DoesNotExist:
                raise ValidationError({'resultado_equipo_id': 'Equipo no existe.'})
        elif 'resultado_abreviatura' in data:
            try:
                ganador = Equipo.objects.get(abreviatura__iexact=str(data['resultado_abreviatura']).strip())
            except Equipo.DoesNotExist:
                raise ValidationError({'resultado_abreviatura': 'Equipo no existe.'})
        elif 'resultado_nombre' in data:
            try:
                ganador = Equipo.objects.get(nombre__iexact=str(data['resultado_nombre']).strip())
            except Equipo.DoesNotExist:
                raise ValidationError({'resultado_nombre': 'Equipo no existe.'})
        else:
            raise ValidationError('Debes enviar resultado_equipo_id o resultado_abreviatura o resultado_nombre.')

        # Validar que sea uno de los dos equipos del partido
        if ganador.id not in (partido.equipo_local_id, partido.equipo_visitante_id):
            raise ValidationError('El resultado debe ser uno de los equipos que jugaron este partido.')

        # Guardar el resultado del partido
        partido.resultado_real = ganador
        partido.save(update_fields=['resultado_real'])

        # Enviar notificación push a todos los participantes de la quiniela
        try:
            # Crear mensaje de notificación
            title = f"¡Resultado del partido!"
            body = f"{partido.equipo_local.abreviatura} vs {partido.equipo_visitante.abreviatura}: Ganó {ganador.abreviatura}"
            
            # Datos adicionales para la notificación
            notification_data = {
                'tipo': 'resultado_partido',
                'quiniela_id': str(quiniela_id),
                'partido_id': str(partido_id),
                'ganador_id': str(ganador.id),
                'ganador_nombre': ganador.nombre,
                'ganador_abreviatura': ganador.abreviatura,
                'equipo_local': partido.equipo_local.abreviatura,
                'equipo_visitante': partido.equipo_visitante.abreviatura
            }
            
            # Enviar notificación a todos los participantes de la quiniela
            fcm_service.send_notification_to_quiniela_participants(
                quiniela_id=quiniela_id,
                title=title,
                body=body,
                data=notification_data
            )
            
        except Exception as e:
            # Log del error pero no fallar la operación principal
            logger.error(f"Error al enviar notificación push: {e}")

        return Response(PartidoReadSerializer(partido).data, status=200)


class EquipoViewSet(viewsets.ModelViewSet):
    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer
    permission_classes = [permissions.AllowAny]  # Cambiar a IsAuthenticatedOrReadOnly si quieres proteger POST/PUT

class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"mensaje": "Usuario creado correctamente"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CambiarMostrarEleccionesView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            quiniela = Quiniela.objects.get(pk=pk)
        except Quiniela.DoesNotExist:
            return Response({'error': 'Quiniela no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        mostrar = request.data.get('mostrar_elecciones')
        if mostrar is None:
            return Response({'error': 'Falta el campo mostrar_elecciones'}, status=status.HTTP_400_BAD_REQUEST)

        quiniela.mostrar_elecciones = mostrar
        quiniela.save()
        return Response({'mostrar_elecciones': quiniela.mostrar_elecciones}, status=status.HTTP_200_OK)

class UnirseQuinielaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, quiniela_id):
        user = request.user

        try:
            quiniela = Quiniela.objects.get(id=quiniela_id)
        except Quiniela.DoesNotExist:
            return Response({"error": "La quiniela no existe"}, status=status.HTTP_404_NOT_FOUND)

        # Evitar que el mismo usuario se una más de una vez
        already_joined = Participante.objects.filter(usuario=user, quiniela=quiniela).exists()
        if not already_joined:
            Participante.objects.create(usuario=user, quiniela=quiniela)
            mensaje = f"{user.username} se unió a la quiniela '{quiniela.nombre}'"
            
            # Enviar notificación push al creador de la quiniela
            try:
                if quiniela.creada_por != user:  # No notificar si se une el creador
                    title = f"👥 Nuevo Participante en {quiniela.nombre}"
                    body = f"{user.username} se ha unido a tu quiniela"
                    data = {
                        'type': 'nuevo_participante',
                        'quiniela_id': quiniela.id,
                        'quiniela_nombre': quiniela.nombre,
                        'usuario_nuevo': user.username
                    }
                    
                    fcm_service.send_notification_to_user(
                        user_id=quiniela.creada_por.id,
                        title=title,
                        body=body,
                        data=data
                    )
                    logger.info(f"Notificación de nuevo participante enviada a {quiniela.creada_por.username}")
            except Exception as e:
                logger.error(f"Error enviando notificación de nuevo participante: {e}")
        else:
            mensaje = f"{user.username} ya está unido a la quiniela '{quiniela.nombre}'"

        # Mostrar todos los participantes actualizados
        participantes = Participante.objects.filter(quiniela=quiniela)
        serializer = ParticipanteSerializer(participantes, many=True)
    
        return Response({
            "mensaje": mensaje,
            "participantes": serializer.data
        }, status=status.HTTP_200_OK)

class QuinielaListCreateView(generics.ListCreateAPIView):
    queryset = Quiniela.objects.all()
    serializer_class = QuinielaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creada_por=self.request.user)
        
        # Crear participante automáticamente
        quiniela = serializer.instance
        Participante.objects.create(
            usuario=self.request.user,
            quiniela=quiniela
        )
        
        # Enviar notificación push a todos los usuarios registrados
        try:
            title = f"🏈 Nueva Quiniela: {quiniela.nombre}"
            body = f"Se ha creado una nueva quiniela con apuesta de \${quiniela.apuesta_individual}"
            data = {
                'type': 'nueva_quiniela',
                'quiniela_id': quiniela.id,
                'quiniela_nombre': quiniela.nombre,
                'apuesta': str(quiniela.apuesta_individual)
            }
            
            fcm_service.send_notification_to_all_users(
                title=title,
                body=body,
                data=data
            )
            logger.info(f"Notificación de nueva quiniela enviada: {quiniela.nombre}")
        except Exception as e:
            logger.error(f"Error enviando notificación de nueva quiniela: {e}")

class QuinielaRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = Quiniela.objects.all()
    serializer_class = QuinielaSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        quiniela = self.get_object()

        if quiniela.creada_por != request.user:
            return Response({"error": "No tienes permiso para eliminar esta quiniela"}, status=status.HTTP_403_FORBIDDEN)

        return self.destroy(request, *args, **kwargs)

class DetalleQuinielaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            quiniela = Quiniela.objects.get(pk=pk)
        except Quiniela.DoesNotExist:
            return Response({"error": "Quiniela no encontrada"}, status=404)

        serializer = QuinielaSerializer(quiniela)
        return Response(serializer.data)
    
class EleccionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EleccionCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            elecciones = serializer.save()
            
            # Enviar notificación push al creador de la quiniela
            try:
                quiniela_id = serializer.validated_data['quiniela_id']
                quiniela = Quiniela.objects.get(id=quiniela_id)
                
                if quiniela.creada_por != request.user:  # No notificar si el creador hace sus elecciones
                    title = f"🎯 Elecciones Realizadas en {quiniela.nombre}"
                    body = f"{request.user.username} ha realizado sus elecciones"
                    data = {
                        'type': 'elecciones_realizadas',
                        'quiniela_id': quiniela_id,
                        'quiniela_nombre': quiniela.nombre,
                        'usuario': request.user.username
                    }
                    
                    fcm_service.send_notification_to_user(
                        user_id=quiniela.creada_por.id,
                        title=title,
                        body=body,
                        data=data
                    )
                    logger.info(f"Notificación de elecciones realizadas enviada a {quiniela.creada_por.username}")
            except Exception as e:
                logger.error(f"Error enviando notificación de elecciones: {e}")
            
            return Response({"detalle": "Elecciones guardadas correctamente."}, status=201)
        return Response(serializer.errors, status=400)


class MisEleccionesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, quiniela_id):
        usuario = request.user
        try:
            participante = Participante.objects.get(usuario=usuario, quiniela_id=quiniela_id)
        except Participante.DoesNotExist:
            return Response({"detail": "No participas en esta quiniela."}, status=400)

        elecciones = Eleccion.objects.filter(participante=participante).select_related('partido', 'equipo_elegido', 'partido__equipo_local', 'partido__equipo_visitante', 'partido__resultado_real')
        data = [
            {
                "partido_id": e.partido.id,
                "equipo_local": EquipoSerializer(e.partido.equipo_local).data,
                "equipo_visitante": EquipoSerializer(e.partido.equipo_visitante).data,
                "equipo_elegido": EquipoSerializer(e.equipo_elegido).data,
                "resultado_real": EquipoSerializer(e.partido.resultado_real).data if e.partido.resultado_real else None
            }
            for e in elecciones
        ]
        return Response(data)
    
class EleccionesDeOtrosQuinielaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, quiniela_id):
        if not Participante.objects.filter(usuario=request.user, quiniela_id=quiniela_id).exists():
            return Response({"detail": "No participas en esta quiniela."}, status=403)

        participantes = Participante.objects.filter(quiniela_id=quiniela_id).select_related('usuario')
        data = []

        for participante in participantes:
            elecciones = Eleccion.objects.filter(participante=participante).select_related(
        'partido', 'equipo_elegido', 'partido__equipo_local', 'partido__equipo_visitante', 'partido__resultado_real'
    )
            data.append({
                "participante": participante.usuario.username,
                "elecciones": [
                    {
                        "partido_id": e.partido.id,
                "equipo_local": EquipoSerializer(e.partido.equipo_local).data,
                "equipo_visitante": EquipoSerializer(e.partido.equipo_visitante).data,
                "equipo_elegido": EquipoSerializer(e.equipo_elegido).data,
                "resultado_real": EquipoSerializer(e.partido.resultado_real).data if e.partido.resultado_real else None
                    } for e in elecciones
                ]
            })

        return Response(data)
    
class EditarFechaLimiteView(generics.UpdateAPIView):
    queryset = Quiniela.objects.all()
    serializer_class = FechaLimiteSerializer
    permission_classes = [IsAuthenticated, EsCreadorDeQuiniela]

class RankingQuinielaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, quiniela_id):
        try:
            quiniela = Quiniela.objects.get(id=quiniela_id)
        except Quiniela.DoesNotExist:
            return Response({"error": "Quiniela no encontrada"}, status=404)

        # Filtrar partidos jugados (con resultado registrado)
        partidos_con_resultado = Partido.objects.filter(quiniela=quiniela, resultado_real__isnull=False)
        total_jugados = partidos_con_resultado.count()

        # Obtener elecciones de esos partidos
        elecciones = Eleccion.objects.filter(partido__in=partidos_con_resultado).select_related('participante', 'partido', 'participante__usuario')

        ranking = {}

        for eleccion in elecciones:
            username = eleccion.participante.usuario.username
            if username not in ranking:
                ranking[username] = {
                    "usuario": username,
                    "aciertos": 0,
                }

            if eleccion.equipo_elegido == eleccion.partido.resultado_real:
                ranking[username]["aciertos"] += 1

        # Convertir a lista y calcular porcentaje
        resultados = []
        for r in ranking.values():
            r["partidos_jugados"] = total_jugados
            r["porcentaje"] = round((r["aciertos"] / total_jugados) * 100, 2) if total_jugados > 0 else 0.0
            resultados.append(r)

        resultados.sort(key=lambda x: x["aciertos"], reverse=True)

        return Response(resultados)

class FCMTokenView(APIView):
    """
    Vista para manejar tokens FCM de usuarios
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        POST /api/fcm-tokens/
        Registra o actualiza un token FCM para el usuario autenticado
        """
        serializer = FCMTokenCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            token = serializer.save()
            return Response({
                'mensaje': 'Token FCM registrado exitosamente',
                'token_id': token.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        """
        GET /api/fcm-tokens/
        Obtiene todos los tokens FCM del usuario autenticado
        """
        tokens = FCMToken.objects.filter(usuario=request.user, activo=True)
        serializer = FCMTokenSerializer(tokens, many=True)
        return Response(serializer.data)
    
    def delete(self, request):
        """
        DELETE /api/fcm-tokens/
        Desactiva un token FCM específico
        """
        token_value = request.data.get('token')
        if not token_value:
            return Response({'error': 'Se requiere el campo token'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = FCMToken.objects.get(
                usuario=request.user,
                token=token_value,
                activo=True
            )
            token.activo = False
            token.save()
            return Response({'mensaje': 'Token FCM desactivado exitosamente'})
        except FCMToken.DoesNotExist:
            return Response({'error': 'Token no encontrado'}, status=status.HTTP_404_NOT_FOUND)

class FCMTokenDetailView(APIView):
    """
    Vista para manejar un token FCM específico
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request, token_id):
        """
        PUT /api/fcm-tokens/<token_id>/
        Actualiza un token FCM específico
        """
        try:
            token = FCMToken.objects.get(id=token_id, usuario=request.user)
        except FCMToken.DoesNotExist:
            return Response({'error': 'Token no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = FCMTokenSerializer(token, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, token_id):
        """
        DELETE /api/fcm-tokens/<token_id>/
        Desactiva un token FCM específico
        """
        try:
            token = FCMToken.objects.get(id=token_id, usuario=request.user)
            token.activo = False
            token.save()
            return Response({'mensaje': 'Token FCM desactivado exitosamente'})
        except FCMToken.DoesNotExist:
            return Response({'error': 'Token no encontrado'}, status=status.HTTP_404_NOT_FOUND)

class TestNotificationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            title = request.data.get('title', 'Notificación de Prueba')
            body = request.data.get('body', 'Esta es una notificación de prueba')
            
            # Enviar notificación de prueba al usuario actual
            success = fcm_service.send_notification_to_user(
                user_id=request.user.id,
                title=title,
                body=body
            )
            
            if success:
                return Response({
                    'mensaje': 'Notificación de prueba enviada exitosamente',
                    'usuario': request.user.username
                }, status=200)
            else:
                return Response({
                    'mensaje': 'Error al enviar notificación de prueba',
                    'usuario': request.user.username
                }, status=500)
                
        except Exception as e:
            logger.error(f"Error en notificación de prueba: {e}")
            return Response({
                'error': 'Error interno del servidor'
            }, status=500)


class TestAuthView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Endpoint simple para probar autenticación"""
        return Response({
            'mensaje': 'Autenticación exitosa',
            'usuario': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'is_active': request.user.is_active
            },
            'timestamp': datetime.now().isoformat()
        }, status=200)
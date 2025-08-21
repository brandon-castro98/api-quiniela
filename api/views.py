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
from .serializer import EquipoSerializer, ResultadoPartidoSerializer, UserRegisterSerializer, QuinielaSerializer, ParticipanteSerializer, PartidoSerializer, EleccionCreateSerializer, FechaLimiteSerializer, PartidoReadSerializer, PartidoWriteByIdSerializer, PartidoWriteByTextSerializer
from .permissions import EsCreadorDeQuiniela

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

        # CORRIGE AQUÍ: Guarda la abreviatura (o nombre, o id, según tu lógica)
        partido.resultado_real = ganador  # <-- Cambia esto
        partido.save(update_fields=['resultado_real'])

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
        return Response(QuinielaSerializer(quiniela).data)

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

class QuinielaRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = Quiniela.objects.all()
    serializer_class = QuinielaSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        quiniela = self.get_object()

        if quiniela.creada_por != request.user:
            return Response({"error": "No tienes permiso para eliminar esta quiniela"}, status=status.HTTP_403_FORBIDDEN)

        return self.destroy(request, *args, **kwargs)

class CrearPartidoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, quiniela_id):
        try:
            quiniela = Quiniela.objects.get(id=quiniela_id)
        except Quiniela.DoesNotExist:
            return Response({"error": "Quiniela no encontrada"}, status=404)

        # Solo el creador puede crear partidos
        if quiniela.creada_por != request.user:
            return Response({"error": "No tienes permiso para agregar partidos a esta quiniela"}, status=403)

        data = request.data.copy()
        data["quiniela"] = quiniela.id

        serializer = PartidoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
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

class HacerEleccionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, quiniela_id, partido_id):
        try:
            quiniela = Quiniela.objects.get(id=quiniela_id)
        except Quiniela.DoesNotExist:
            return Response({"detail": "Quiniela no encontrada."}, status=404)

        if quiniela.fecha_limite and timezone.now() > quiniela.fecha_limite:
            return Response({"detail": "Ya no se pueden hacer elecciones. Fecha límite superada."}, status=403)

        # lógica para guardar elección aquí...

        return Response({"detail": "Elección registrada."})
    
class RegistrarResultadoPartidoView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, partido_id):
        try:
            partido = Partido.objects.select_related('quiniela').get(id=partido_id)
        except Partido.DoesNotExist:
            return Response({"error": "Partido no encontrado"}, status=404)

        if partido.quiniela.creada_por != request.user:
            return Response({"detail": "No tienes permiso para editar este resultado."}, status=403)

        serializer = ResultadoPartidoSerializer(partido, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detalle": "Resultado guardado correctamente."})
        return Response(serializer.errors, status=400)
    
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
    
class CambiarMostrarEleccionesView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, quiniela_id):
        try:
            quiniela = Quiniela.objects.get(pk=quiniela_id)
        except Quiniela.DoesNotExist:
            return Response({'error': 'Quiniela no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        mostrar = request.data.get('mostrar_elecciones')
        if mostrar is None:
            return Response({'error': 'Falta el campo mostrar_elecciones'}, status=status.HTTP_400_BAD_REQUEST)

        quiniela.mostrar_elecciones = mostrar
        quiniela.save()
        return Response({'mostrar_elecciones': quiniela.mostrar_elecciones}, status=status.HTTP_200_OK)
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, viewsets, permissions
from django.utils import timezone
from .models import Quiniela, Participante, Partido, Eleccion, Equipo
from .serializer import EquipoSerializer, ResultadoPartidoSerializer, UserRegisterSerializer, QuinielaSerializer, ParticipanteSerializer, PartidoSerializer, EleccionCreateSerializer, FechaLimiteSerializer
from .permissions import EsCreadorDeQuiniela

# Create your views here.

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

        elecciones = Eleccion.objects.filter(participante=participante).select_related('partido')
        data = [
            {
                "partido_id": e.partido.id,
                "equipo_local": e.partido.equipo_local,
                "equipo_visitante": e.partido.equipo_visitante,
                "equipo_elegido": e.equipo_elegido,
                "resultado_real": e.partido.resultado_real
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
            elecciones = Eleccion.objects.filter(participante=participante).select_related('partido')
            data.append({
                "participante": participante.usuario.username,
                "elecciones": [
                    {
                        "partido_id": e.partido.id,
                        "equipo_local": e.partido.equipo_local,
                        "equipo_visitante": e.partido.equipo_visitante,
                        "equipo_elegido": e.equipo_elegido,
                        "resultado_real": e.partido.resultado_real
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
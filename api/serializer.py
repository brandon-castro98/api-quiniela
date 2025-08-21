from rest_framework import serializers
from .models import Quiniela, Participante, Partido, Eleccion, Equipo
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user
    
class EquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo
        fields = ['id', 'nombre', 'abreviatura', 'logo_url']

# Lectura de partido (detallado con equipos y resultado)
class PartidoReadSerializer(serializers.ModelSerializer):
    equipo_local = EquipoSerializer()
    equipo_visitante = EquipoSerializer()
    resultado_real = EquipoSerializer()

    class Meta:
        model = Partido
        fields = ['id', 'fecha', 'equipo_local', 'equipo_visitante', 'resultado_real']

# Escritura por IDs (más estricto/rápido)
class PartidoWriteByIdSerializer(serializers.Serializer):
    equipo_local_id = serializers.IntegerField()
    equipo_visitante_id = serializers.IntegerField()
    fecha = serializers.DateTimeField()

# Escritura por texto (fallback si hoy tu front escribe nombres/abrev)
class PartidoWriteByTextSerializer(serializers.Serializer):
    # Puedes mandar nombres o abreviaturas
    equipo_local_nombre = serializers.CharField(required=False)
    equipo_local_abreviatura = serializers.CharField(required=False)
    equipo_visitante_nombre = serializers.CharField(required=False)
    equipo_visitante_abreviatura = serializers.CharField(required=False)
    fecha = serializers.DateTimeField()
    
class PartidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partido
        fields = '__all__'

class EleccionSerializer(serializers.ModelSerializer):
    equipo_elegido = EquipoSerializer()
    class Meta:
        model = Eleccion
        fields = ['id', 'partido', 'equipo_elegido']

class EleccionInputSerializer(serializers.Serializer):
    partido_id = serializers.IntegerField()
    equipo_elegido = serializers.IntegerField()

class EleccionCreateSerializer(serializers.Serializer):
    quiniela_id = serializers.IntegerField()
    elecciones = EleccionInputSerializer(many=True)

    def validate(self, data):
        quiniela_id = data['quiniela_id']
        user = self.context['request'].user

        try:
            participante = Participante.objects.get(usuario=user, quiniela_id=quiniela_id)
        except Participante.DoesNotExist:
            raise serializers.ValidationError("No estás inscrito en esta quiniela.")

        partidos_ids = Partido.objects.filter(quiniela_id=quiniela_id).values_list('id', flat=True)
        for eleccion in data['elecciones']:
            if eleccion['partido_id'] not in partidos_ids:
                raise serializers.ValidationError(f"El partido {eleccion['partido_id']} no pertenece a la quiniela.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        quiniela_id = validated_data['quiniela_id']
        elecciones = validated_data['elecciones']

        participante = Participante.objects.get(usuario=user, quiniela_id=quiniela_id)

        objetos_creados = []
        for e in elecciones:
            equipo = Equipo.objects.get(pk=e['equipo_elegido'])
            eleccion, created = Eleccion.objects.update_or_create(
                participante=participante,
                partido_id=e['partido_id'],
                defaults={'equipo_elegido': equipo}
            )
            objetos_creados.append(eleccion)

        return objetos_creados

class QuinielaSerializer(serializers.ModelSerializer):
     creada_por = serializers.ReadOnlyField(source='creada_por.username')
     participantes = serializers.StringRelatedField(many=True, read_only=True)
     partidos = PartidoSerializer(many=True, read_only=True)
     mostrar_elecciones = serializers.BooleanField(default=False)


     class Meta:
        model = Quiniela
        fields = ['id', 'nombre', 'apuesta_individual', 'creada_por', 'fecha_creacion', 'participantes', 'partidos', 'mostrar_elecciones']

class ParticipanteSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username')

    class Meta:
        model = Participante
        fields = ['id', 'username', 'ya_selecciono']

class FechaLimiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiniela
        fields = ['fecha_limite']

class ResultadoPartidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partido
        fields = ['resultado_real']

from rest_framework import serializers
from .models import Quiniela, Participante, Partido, Eleccion, Equipo
from django.contrib.auth import get_user_model
from .models import FCMToken
from django.utils import timezone

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

class ParticipanteSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField()
    
    class Meta:
        model = Participante
        fields = ['id', 'usuario', 'ya_selecciono']

class QuinielaSerializer(serializers.ModelSerializer):
    creada_por = serializers.StringRelatedField()
    participantes = ParticipanteSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiniela
        fields = ['id', 'nombre', 'apuesta_individual', 'creada_por', 'fecha_creacion', 'fecha_limite', 'mostrar_elecciones', 'participantes']

class FechaLimiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiniela
        fields = ['fecha_limite']

class FCMTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMToken
        fields = ['id', 'token', 'dispositivo', 'plataforma', 'activo', 'fecha_creacion', 'ultima_actividad']
        read_only_fields = ['id', 'fecha_creacion', 'ultima_actividad']

    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance.ultima_actividad = timezone.now()
        return super().update(instance, validated_data)

class FCMTokenCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMToken
        fields = ['token', 'dispositivo', 'plataforma']

    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        
        # Verificar si ya existe un token para este usuario y dispositivo
        existing_token = FCMToken.objects.filter(
            usuario=validated_data['usuario'],
            token=validated_data['token']
        ).first()
        
        if existing_token:
            # Actualizar token existente
            existing_token.dispositivo = validated_data.get('dispositivo', existing_token.dispositivo)
            existing_token.plataforma = validated_data.get('plataforma', existing_token.plataforma)
            existing_token.activo = True
            existing_token.save()
            return existing_token
        
        return super().create(validated_data)

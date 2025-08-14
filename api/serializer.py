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
        fields = '__all__'
    
class PartidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partido
        fields = '__all__'

class EleccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eleccion
        fields = ['id', 'partido', 'equipo_seleccionado']

class EleccionInputSerializer(serializers.Serializer):
    partido_id = serializers.IntegerField()
    equipo_elegido = serializers.CharField()

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
            eleccion, created = Eleccion.objects.update_or_create(
                participante=participante,
                partido_id=e['partido_id'],
                defaults={'equipo_elegido': e['equipo_elegido']}
            )
            objetos_creados.append(eleccion)

        return objetos_creados

class QuinielaSerializer(serializers.ModelSerializer):
     creada_por = serializers.ReadOnlyField(source='creada_por.username')
     participantes = serializers.StringRelatedField(many=True, read_only=True)
     partidos = PartidoSerializer(many=True, read_only=True)

     class Meta:
        model = Quiniela
        fields = ['id', 'nombre', 'apuesta_individual', 'creada_por', 'fecha_creacion', 'participantes', 'partidos']

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

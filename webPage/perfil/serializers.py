

from rest_framework import serializers
from auth_app.models import Profile
from auth_app.serializers import UserSerializer
from rest_framework.authtoken.models import Token

class ProfileInfoSerializer(serializers.ModelSerializer):
    # Aquí accedemos al campo 'user' del modelo Profile, que es un OneToOneField con el modelo User
    user = UserSerializer()
    key = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'avatar', 'cover', 'key']

    def get_key(self, obj):
        # Acceder al usuario asociado al perfil
        user = obj.user
        # Obtener o crear el token de autenticación para ese usuario
        token, created = Token.objects.get_or_create(user=user)
        return token.key
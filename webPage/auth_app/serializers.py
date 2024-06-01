from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile
from threads.serializers import ThreadSerializer, CommentSerializer, BoostSerializer

class UserSerializer(serializers.ModelSerializer):


    class Meta:

        model = User
        fields = ['id', 'username', 'email']

class EditUserSerializer(serializers.ModelSerializer):


    class Meta:

        model = User
        fields = ['username', 'email']

class EditProfileSerializer(serializers.ModelSerializer):


    class Meta:

        model = Profile
        exclude = ['user', 'id']



class ProfileSerializer(serializers.ModelSerializer):


    class Meta:

        model = Profile
        exclude = ['user']

class ProfileImageSerializer(serializers.ModelSerializer):

    class Meta:

        model = Profile
        fields = ['avatar', 'cover']

class ProfileDetailSerializer(serializers.Serializer):
    user = UserSerializer(many=False)
    profile = ProfileSerializer(many=False)
    threads_count = serializers.IntegerField()
    threads = ThreadSerializer(many=True)
    comments_count = serializers.IntegerField()
    comments = CommentSerializer(many=True)    
    boosts_count = serializers.IntegerField()
    boosts = BoostSerializer(many=True)
    active_filter = serializers.CharField()
    active_order = serializers.CharField()
    

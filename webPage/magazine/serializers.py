from rest_framework import serializers
from .models import Magazine
from django.contrib.auth import get_user_model
from .models import Subscription
User = get_user_model()


class CreateMagazineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Magazine
        fields = ['id','name', 'title', 'description', 'rules','author']
        extra_kwargs = {
            "author": {"read_only": True},
        }

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["author"] = user
        
        return super().create(validated_data)

class MagazineSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    user_has_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Magazine
        fields = ['id','name', 'title', 'author', 'description', 'rules', 'publish_date', 'subscriptions_count', 'threads_count', 'comments_count','user_has_subscribed']
    
    def get_author(self, obj):
        return {
            "id": obj.author.id,
            "username": obj.author.username,
            "avatar": obj.author.profile.avatar.url
        }
    
    def get_user_has_subscribed(self, obj):
        user = self.context.get('user')
        if user is None:
            return None  # Devuelve False si no hay usuario autenticado
        return Subscription.objects.filter(user=user, magazine=obj).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    status = serializers.CharField(max_length=20, read_only=True, default='subscribed')
    user_id = serializers.ReadOnlyField(source='user.id')
    magazine_id = serializers.ReadOnlyField(source='magazine.id')

    class Meta:
        model = Subscription
        fields = ['id','status', 'user_id', 'magazine_id']

class UnsubscriptionSerializer(serializers.ModelSerializer):
    status = serializers.CharField(max_length=20, read_only=True, default='unsubscribed')
    user_id = serializers.ReadOnlyField(source='user.id')
    magazine_id = serializers.ReadOnlyField(source='magazine.id')

    class Meta:
        model = Subscription
        fields = ['id','status', 'user_id', 'magazine_id']
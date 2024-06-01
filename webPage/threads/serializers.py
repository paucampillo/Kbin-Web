"""
This file contains the serializers for the Threads app.
"""

from urllib import request
from django.forms import ValidationError
from django.http import Http404
from rest_framework import serializers
from .models import Thread, Boost, Vote, Comment, CommentReply


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ["id", "user", "thread", "comment", "reply", "vote_type"]


class BoostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boost
        fields = ["id", "user", "thread"]


class CreateThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ["id", "title", "url", "author", "body", "magazine"]
        extra_kwargs = {
            "url": {"required": False},
            "author": {"read_only": True},
        }

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["author"] = user
        url = validated_data.get("url")
        if url:
            validated_data["is_link"] = True
        return super().create(validated_data)


class ThreadSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    magazine = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    user_has_disliked = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = [
            "id",
            "title",
            "url",
            "body",
            "created_at",
            "updated_at",
            "is_link",
            "num_likes",
            "num_dislikes",
            "num_comments",
            "num_points",
            "author",
            "magazine",
            "user_has_liked",
            "user_has_disliked",
        ]
    
    def get_author(self, obj):
        return {
            "id": obj.author.id,
            "username": obj.author.username
        }

    def get_magazine(self, obj):
        return {
            "id": obj.magazine.id,
            "name": obj.magazine.name
        }

    def get_user_has_liked(self, obj):
        user = self.context.get('user')
        if user is None:
            return None # Devuelve None si no hay usuario autenticado
        return Vote.objects.filter(user=user, thread=obj, vote_type='like').exists()
    
    def get_user_has_disliked(self, obj):
        user = self.context.get('user')
        if user is None:
            return None # Devuelve None si no hay usuario autenticado
        return Vote.objects.filter(user=user, thread=obj, vote_type='dislike').exists()


class EditThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ["title", "body"]
        extra_kwargs = {
            "title": {"required": False},
            "body": {"required": False},
        }



class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReply
        fields = ["id", "author", "thread", "parent_comment", "parent_reply", "body"]
        extra_kwargs = {
            "author": {"read_only": True},
            "parent_comment": {"required": False},
            "parent_reply": {"required": False},
        }

    def create(self, validated_data):
        # Obtiene el usuario de la solicitud
        user = self.context["request"].user
        # Obtiene el thread_id
        thread_id = validated_data["thread"].id
        if not Thread.objects.filter(id=thread_id).exists():
            raise Http404("Thread does not exist")

        # Verificar si parent_comment es nulo y parent_reply también lo es
        if "parent_comment" not in validated_data and "parent_reply" not in validated_data:
            # Crear un nuevo comentario
            reply = Comment.objects.create(
                author=user,
                thread_id=thread_id,
                **validated_data
            )
            return reply

        # Verificar si parent_comment no es nulo pero parent_reply sí lo es
        if "parent_comment" in validated_data and "parent_reply" not in validated_data:
            parent_comment = validated_data["parent_comment"]
            # Comprovar thread_id del parent_comment
            if parent_comment.thread.id != thread_id:
                raise Http404("Parent comment and thread do not belong to the same thread")
            reply_level = 1  # Es una respuesta a un comentario
            reply = CommentReply.objects.create(
                author=user,
                thread_id=thread_id,
                reply_level=reply_level,
                **validated_data
            )
            return reply

        # Verificar si parent_comment es nulo pero parent_reply no lo es
        if "parent_comment" not in validated_data and "parent_reply" in validated_data:
            raise Http404("Cannot reply to a reply without a parent comment.")

        # Verificar si ambos parent_comment y parent_reply no son nulos
        if "parent_comment" in validated_data and "parent_reply" in validated_data:
            parent_comment = validated_data["parent_comment"]
            parent_reply = validated_data["parent_reply"]
            # Comprobar si el parent_reply pertenece al mismo hilo que el parent_comment y al hilo actual
            if parent_reply.parent_comment.id != parent_comment.id:
                raise Http404("Parent reply does not belong to the same comment.")
            if parent_reply.thread.id != thread_id:
                raise Http404("Parent reply does not belong to the same thread.")
            if parent_comment.thread.id != thread_id:
                raise Http404("Parent comment does not belong to the same thread.")
            # Verificar que el parent_reply pertenece al mismo hilo que el parent_comment
            reply_level = parent_reply.reply_level + 1  # Es una respuesta a una respuesta
            reply = CommentReply.objects.create(
                author=user,
                thread_id=thread_id,
                reply_level=reply_level,
                **validated_data
            )
            return reply


    
class EditCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["body"]
        extra_kwargs = {
            "body": {"required": False},
        }

class CommentReplySerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    magazine = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    user_has_disliked = serializers.SerializerMethodField()

    class Meta:
        model = CommentReply
        fields = [
            "id",
            "body",
            "created_at",
            "updated_at",
            "num_likes",
            "num_dislikes",
            "num_replies",
            "author",
            "magazine",
            "user_has_liked",
            "user_has_disliked",
            "parent_comment",
            "parent_reply",
            "thread_id",
            "reply_level",
        ]
    def get_author(self, obj):
        return {
            "id": obj.author.id,
            "username": obj.author.username
        }
    def get_magazine(self, obj):
        return {
            "id": obj.thread.magazine.id,
            "name": obj.thread.magazine.name
        }
    def get_user_has_liked(self, obj):
        user = self.context.get('user')
        if user is None:
            return None # Devuelve None si no hay usuario autenticado
        return Vote.objects.filter(user=user, reply=obj, vote_type='like').exists()
    def get_user_has_disliked(self, obj):
        user = self.context.get('user')
        if user is None:
            return None
        return Vote.objects.filter(user=user, reply=obj, vote_type='dislike').exists()
    

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    magazine = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    user_has_disliked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "body",
            "created_at",
            "updated_at",
            "num_likes",
            "num_dislikes",
            "num_replies",
            "author",
            "magazine",
            "thread_id",
            "user_has_liked",
            "user_has_disliked",
            "replies",
        ]
    def get_author(self, obj):
        return {
            "id": obj.author.id,
            "username": obj.author.username
        }
    
    def get_magazine(self, obj):
        return {
            "id": obj.thread.magazine.id,
            "name": obj.thread.magazine.name
        }
    
    def get_user_has_liked(self, obj):
        user = self.context.get('user')
        if user is None:
            return None # Devuelve None si no hay usuario autenticado
        return Vote.objects.filter(user=user, comment=obj ,vote_type='like').exists()
    
    def get_user_has_disliked(self, obj):
        user = self.context.get('user')
        if user is None:
            return None # Devuelve None si no hay usuario autenticado
        return Vote.objects.filter(user=user, comment=obj, vote_type='dislike').exists()
    
    def get_replies(self, obj):
        replies = CommentReply.objects.filter(parent_comment=obj)
        return CommentReplySerializer(replies, many=True, context=self.context).data
    


class CreateCommentReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReply
        fields = ["id", "author", "thread", "parent_comment", "parent_reply", "body"]
        extra_kwargs = {
            "author": {"read_only": True},
        }

    def create(self, validated_data):
        # Obtiene el usuario de la solicitud
        user = self.context["request"].user
        # Obtiene el thread_id
        thread_id = validated_data["thread"].id
        if not Thread.objects.filter(id=thread_id).exists():
            raise Http404("Thread does not exist")
        
        # Obtiene el parent_comment_id 
        parent_comment_id = validated_data["parent_comment"].id
        if not Comment.objects.filter(id=parent_comment_id).exists():
            raise Http404("Parent comment does not exist")
        
        # Obtiene el parent_reply_id
        parent_reply_id = validated_data["parent_reply"].id
        if not CommentReply.objects.filter(id=parent_reply_id).exists():
            raise Http404("Parent reply does not exist")

        # Obtener el parent_comment
        parent_comment = Comment.objects.get(pk=parent_comment_id)
        # Ontener el parent_reply
        parent_reply = CommentReply.objects.get(pk=parent_reply_id)
        # Obtener el thread_id del parent_comment
        if parent_comment.thread_id != thread_id:
            raise Http404("Parent comment and thread do not belong to the same thread")
        # Obtener el thread_id del parent_reply
        if parent_reply.thread_id != thread_id:
            raise Http404("Parent reply and thread do not belong to the same thread")
        

            
        # Crear la respuesta al comentario con el autor, el cuerpo de la respuesta, el parent_comment_id, el thread_id, el reply_level y el parent_reply
        reply = CommentReply.objects.create(
            author=user, 
            thread_id=thread_id, 
            reply_level=reply_level, 
            parent_reply=parent_reply,
            **validated_data
        )
        return reply


class CommentReplyReplySerializer(serializers.ModelSerializer):
    magazine = serializers.ReadOnlyField(source="thread.magazine.id")
    class Meta:
        model = CommentReply
        fields = "__all__"

class CreateCommentReplyReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReply
        fields = ["id", "author", "body"]
        extra_kwargs = {
            "author": {"read_only": True},
        }

    def create(self, validated_data):
        # Obtiene el usuario de la solicitud
        user = self.context["request"].user
        # Obtiene el thread_id de la URL
        thread_id = self.context["view"].kwargs["thread_id"]
        # Obtiene el parent_reply_id de la URL
        parent_reply_id = self.context["view"].kwargs["commentreply_id"]
        # Obtiene el parent_comment_id de los datos validados
        parent_comment_id = self.context["view"].kwargs["comment_id"]
        
        # Comprobar si existe el parent_reply
        try:
            parent_reply = CommentReply.objects.get(id=parent_reply_id)
        except CommentReply.DoesNotExist:
            raise Http404("Parent reply does not exist")
        
        # Comprobar si existe el parent_comment
        try:
            parent_comment = Comment.objects.get(id=parent_comment_id)
        except Comment.DoesNotExist:
            raise Http404("Parent comment does not exist")
        
        # Comprobar si el parent_reply es realmente una respuesta al parent_comment
        if parent_reply.parent_comment != parent_comment:
            raise Http404("Parent reply is not a reply to the parent comment")
        
        # Comprobar si el parent_reply y el parent_comment pertenecen al mismo thread
        if thread_id != parent_comment.thread_id or thread_id != parent_reply.thread_id:
            raise Http404("Parent reply and parent comment do not belong to the same thread")

        
        # Obtiene el thread_id del parent_comment
        thread_id = parent_comment.thread_id
        # Establece el reply_level como el nivel del parent_reply + 1
        reply_level = parent_reply.reply_level + 1
        
        # Crea la respuesta al comentario con el autor, el cuerpo de la respuesta, el parent_comment_id, el thread_id, el reply_level y el parent_reply
        reply = CommentReply.objects.create(
            author=user, 
            parent_comment=parent_comment, 
            thread_id=thread_id, 
            reply_level=reply_level, 
            parent_reply=parent_reply,
            **validated_data
        )
        return reply
    
class EditCommentReplyReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReply
        fields = ["body"]
        extra_kwargs = {
            "body": {"required": False},
        }
    
class EditCommentReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["body"]
        extra_kwargs = {
            "body": {"required": False},
        }


class SearchSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    magazine = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    user_has_disliked = serializers.SerializerMethodField()


    class Meta:
        """
        Meta class for the serializer
        """

        model = Thread
        fields = [
            "id",
            "title",
            "url",
            "body",
            "created_at",
            "updated_at",
            "is_link",
            "num_likes",
            "num_dislikes",
            "num_comments",
            "num_points",
            "author",
            "magazine",
            "user_has_liked",
            "user_has_disliked",
        ]

    def get_author(self, obj):
        return {
            "id": obj.author.id,
            "username": obj.author.username
        }

    def get_magazine(self, obj):
        return {
            "id": obj.magazine.id,
            "name": obj.magazine.name
        }

    def get_user_has_liked(self, obj):
        user = self.context.get('user')
        if user is None:
            return None # Devuelve None si no hay usuario autenticado
        return Vote.objects.filter(user=user, thread=obj, vote_type='like').exists()
    
    def get_user_has_disliked(self, obj):
        user = self.context.get('user')
        if user is None:
            return None # Devuelve None si no hay usuario autenticado
        return Vote.objects.filter(user=user, thread=obj, vote_type='dislike').exists()

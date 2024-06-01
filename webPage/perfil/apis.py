from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User  # Importar el modelo User
from threads.models import Thread, Comment,Boost, CommentReply
from threads.serializers import ThreadSerializer, CommentSerializer
from .serializers import ProfileInfoSerializer
from rest_framework.authentication import TokenAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from itertools import chain
from django.db.models import Q, Case, When

class UserInfoView(generics.RetrieveAPIView):
    serializer_class = ProfileInfoSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        return user.profile

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user if self.request.user.is_authenticated else None
        return context
    

class UserThreadsView(generics.ListAPIView):
    serializer_class = ThreadSerializer
    authentication_classes = [TokenAuthentication]
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "filter",
                openapi.IN_QUERY,
                description="Filter threads by 'all', 'threads', or 'links'",
                type=openapi.TYPE_STRING,
                default="all",
            ),
            openapi.Parameter(
                "order_by",
                openapi.IN_QUERY,
                description="Order threads by 'created_at', 'points', or 'num_comments'",
                type=openapi.TYPE_STRING,
                default="created_at",
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        return get_filtered_queryset(self.request, user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user if self.request.user.is_authenticated else None
        return context
    
def get_filtered_queryset(request, profile_user):
    queryset = Thread.objects.filter(author=profile_user)
    filter_option = request.GET.get("filter", "all")
    order_by = request.GET.get("order_by", "created_at")

    if filter_option == "threads":
        queryset = queryset.filter(url__isnull=True)
    elif filter_option == "links":
        queryset = queryset.exclude(url__isnull=True)

    if order_by == "points":
        queryset = queryset.order_by("-num_points")
    elif order_by == "num_comments":
        queryset = queryset.order_by("-num_comments")
    else:
        queryset = queryset.order_by("-created_at")

    request.session["filter"] = filter_option
    request.session["order_by"] = order_by

    return queryset


class UserCommentsView(generics.ListAPIView):
    serializer_class = CommentSerializer
    #permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @swagger_auto_schema(
        operation_description="Get comments and replies for a thread",
        manual_parameters=[
            openapi.Parameter(
                "order_by",
                openapi.IN_QUERY,
                description="Order comments by 'newest', 'likes', or 'oldest'",
                type=openapi.TYPE_STRING,
                default="newest",
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        ids = get_filtered_queryset_comments(self.request, user)

        # Convertir la lista de IDs en un QuerySet
        comments_queryset = Comment.objects.filter(id__in=ids)
        replies_queryset = CommentReply.objects.filter(id__in=ids)

        # Usar Q para combinar ambos QuerySets en uno
        combined_queryset = Comment.objects.filter(
            Q(id__in=comments_queryset) | Q(id__in=replies_queryset)
        ).distinct()

        # Mantener el orden original de la lista
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
        combined_queryset = combined_queryset.order_by(preserved)

        return combined_queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user if self.request.user.is_authenticated else None
        return context
from django.db.models import Q


from django.db.models import Q

def get_filtered_queryset_comments(request, profile_user):
    comments = Comment.objects.filter(author=profile_user)
    replies = CommentReply.objects.filter(author=profile_user)

    # Combinar los QuerySets en una lista
    combined_list = list(chain(comments, replies))

    # Obtener el parámetro de ordenación
    order_by = request.GET.get("order_by", "created_at")

    # Ordenar la lista combinada en Python basándose en el criterio seleccionado
    if order_by == "likes":
        sorted_list = sorted(combined_list, key=lambda x: (x.num_likes, -x.created_at.timestamp()), reverse=True)
    elif order_by == "newest":
        sorted_list = sorted(combined_list, key=lambda x: -x.created_at.timestamp())
    else:
        sorted_list = sorted(combined_list, key=lambda x: x.created_at.timestamp())

    # Guardar el criterio de ordenación en la sesión
    request.session["order_by"] = order_by

    # Devolver solo los IDs para convertir luego a QuerySet
    return [obj.id for obj in sorted_list]


class UserBoostsView(generics.ListAPIView):
    serializer_class = ThreadSerializer
    #permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        boosts_user = Boost.objects.filter(user=user)
        return Thread.objects.filter(boost__in=boosts_user).distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user if self.request.user.is_authenticated else None
        return context
    
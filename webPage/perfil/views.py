from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
#from .models import ProfileUser
from threads.models import Thread, Comment,Boost, CommentReply

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User  # Importar el modelo User

from django.db.models import Q
from itertools import chain

from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view,  permission_classes
from rest_framework import permissions

from threads.serializers import ThreadSerializer, CommentSerializer
from auth_app.serializers import UserSerializer, ProfileSerializer, ProfileDetailSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes
from rest_framework.authentication import TokenAuthentication


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

    # Guardar los valores de filtro y orden en la sesión del usuario
    request.session["filter"] = filter_option
    request.session["order_by"] = order_by

    return queryset

def get_filtered_queryset_comments(request, profile_user):
    comments = Comment.objects.filter(author=profile_user)
    replies = CommentReply.objects.filter(author=profile_user)

    # Combinar los QuerySets en una lista
    combined_list = list(chain(comments, replies))

    # Obtener el parámetro de ordenación
    order_by = request.GET.get("order_by", "created_at")

    # Ordenar la lista combinada en Python basándose en el criterio seleccionado
    if order_by == "points":
        sorted_list = sorted(combined_list, key=lambda x: (x.num_likes, -x.created_at.timestamp()), reverse=True)
    elif order_by == "newest":
        sorted_list = sorted(combined_list, key=lambda x: -x.created_at.timestamp())
    else:
        sorted_list = sorted(combined_list, key=lambda x: x.created_at.timestamp())

    # Guardar el criterio de ordenación en la sesión
    request.session["order_by"] = order_by

    return sorted_list

# Create your views here.
def profile_detail(request, user_id):
    # Obtener el objeto del usuario basado en el nombre de usuario
    user  = get_object_or_404(User, id=user_id)

    profile_user = user

    threads = get_filtered_queryset(request, user)

    comments = get_filtered_queryset_comments(request, user)

    key = Token.objects.get_or_create(user=user)
    key = key[0]

   
    #replies = CommentReply.objects.filter(author=user)

    # below for html comments
    #<a href="{% url 'thread_detail' pk=comment.thread.id %}" class="user-inline">{{ comment.thread }}</a>,
    boosts_user = Boost.objects.filter(user=user)

    boosts = Thread.objects.filter(Q(boost__in=boosts_user)).distinct()
    # Get all the threads 

    filter_option = request.session.get("filter", "all")
    order_by = request.session.get("order_by", "created_at")
    #will need that if we wanna view the logged profiles session it needs the boosts list also.
    #so will be like:
    #if (session.log = profiles_user) { return render the html with he boosts list}
    #boosts = Boost.object.filter(user=profile_user)

    # in this may be we can just pass to the html and integer like 0,1,2, depending in which numbers is in the
    # html we will include the threads list, the comments list or the boost list.
    #if(request.headers):
        #if(request.headers["Authorization"]):
         #   if(request.headers["Authorization"] == Token.objects.get_or_create(user = user)):
             #   return Response("200, Ok")
          #  else:
           #     return Response("AAAAAA")
    return render(request, 'profile_detail.html', {'profile_user': profile_user, 'threads': threads, 'comments':comments, 'comments_count': len(comments), 'boosts': boosts, 'active_filter': filter_option, 'active_order': order_by, 'key':key})

def get_details(request, user_id):
    user = get_object_or_404(User, id=user_id)

    profile_user = user

    threads = get_filtered_queryset(request, user)

    comments = get_filtered_queryset_comments(request, user)

    key = Token.objects.get_or_create(user=user)
    key = key[0]

    boosts_user = Boost.objects.filter(user=user)

    boosts = Thread.objects.filter(boost__in=boosts_user).distinct()

    filter_option = request.session.get("filter", "all")
    order_by = request.session.get("order_by", "created_at")

    # Serialize data
    user_serializer = UserSerializer(profile_user)
    threads_serializer = ThreadSerializer(threads, many=True)
    comments_serializer = CommentSerializer(comments, many=True)
    profile_serializer = ProfileSerializer(profile_user.profile)

    data = {
        'user': user_serializer.data,
        'profile': profile_serializer.data,
        'key': key.key,
        'threads_count': len(threads_serializer.data),
        'threads': threads_serializer.data,
        'comments_count': len(comments_serializer.data),
        'comments': comments_serializer.data,
        'boosts_count': len(ThreadSerializer(boosts, many=True).data,),
        'boosts': ThreadSerializer(boosts, many=True).data,
        'active_filter': filter_option,
        'active_order': order_by,
    }
    return data

@swagger_auto_schema(method='get', 
                     responses={200: openapi.Response('Success', ProfileDetailSerializer)},
                     operation_summary='Get profile details',
                     operation_description='Get detailed information about a user profile.')
@api_view(['GET',])
@permission_classes((permissions.AllowAny,))
def profile_detail_api(request, user_id):
    return Response(get_details(request, user_id))

@swagger_auto_schema(method='get', 
                     responses={200: openapi.Response('Success', ProfileDetailSerializer), 401: openapi.Response("detail: Authentication credentials were not provided.")},
                     operation_summary='Get profile details',
                     operation_description='Get detailed information about logged in user\'s profile.')
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@authentication_classes((TokenAuthentication,))
def my_profile_detail_api(request):
    return redirect("/api/profile/" + str(request.user.id) + "/")



    


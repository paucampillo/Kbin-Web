from rest_framework import generics 
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAuthenticatedOrReadOnly
from .models import Magazine, Subscription
from .serializers import MagazineSerializer,CreateMagazineSerializer,SubscriptionSerializer, UnsubscriptionSerializer
from rest_framework.generics import ListCreateAPIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from rest_framework.authentication import TokenAuthentication
from threads.serializers import ThreadSerializer
from threads.models import Thread

class MagazineDetailView(generics.RetrieveAPIView):
    queryset = Magazine.objects.all()
    serializer_class = MagazineSerializer
    authentication_classes = [TokenAuthentication]

    def get_object(self):
        magazine_id = self.kwargs.get('magazine_id')
        return get_object_or_404(Magazine, id=magazine_id)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user if self.request.user.is_authenticated else None
        return context

class MagazineThreadsView(generics.ListAPIView):
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
        magazine_id = self.kwargs['magazine_id']
        magazine = get_object_or_404(Magazine, id=magazine_id)
        return self.get_filtered_queryset(magazine)

    def get_filtered_queryset(self, magazine):
        queryset = Thread.objects.filter(magazine=magazine)
        filter_option = self.request.query_params.get('filter', 'all')
        order_by = self.request.query_params.get('order_by', 'created_at')

        if filter_option == 'threads':
            queryset = queryset.filter(url__isnull=True)
        elif filter_option == 'links':
            queryset = queryset.exclude(url__isnull=True)

        if order_by == 'points':
            queryset = queryset.order_by('-num_points')
        elif order_by == 'num_comments':
            queryset = queryset.order_by('-num_comments')
        else:
            queryset = queryset.order_by('-created_at')

        # Guardar los valores de filtro y orden en la sesión del usuario
        self.request.session['filter'] = filter_option
        self.request.session['order_by'] = order_by

        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user if self.request.user.is_authenticated else None
        return context
    
class MagazineSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, magazine_id):
        """Subscribe a user to a magazine."""
        magazine = get_object_or_404(Magazine, id=magazine_id)
        subscription, created = Subscription.objects.get_or_create(user=request.user, magazine=magazine)

        if not created:
            # The subscription already exists, so we inform the user
            return Response({'status': 'already subscribed', 'user_id': request.user.id, 'magazine_id': magazine_id}, status=status.HTTP_409_CONFLICT)

        # Update the subscription count when a new subscription is created
        magazine.subscriptions_count += 1
        magazine.save()

        # Serialize the subscription data
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, magazine_id):
        """Unsubscribe a user from a magazine."""
        magazine = get_object_or_404(Magazine, id=magazine_id)
        subscription = Subscription.objects.filter(user=request.user, magazine=magazine).first()
        
        if not subscription:
            return Response({'status': 'not subscribed', 'user_id': request.user.id, 'magazine_id': magazine_id}, status=status.HTTP_404_NOT_FOUND)

        subscription.delete()
        magazine.subscriptions_count -= 1
        magazine.save()

        # Return the unsubscribed status
        serializer = UnsubscriptionSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class MagazineList(ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user if self.request.user.is_authenticated else None
        return context

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateMagazineSerializer
        return MagazineSerializer

    def get_queryset(self):
        orderby = self.request.query_params.get("orderby", "subscriptions_count")

        ordering = "-subscriptions_count"  # Default ordering
        if orderby == "threads":
            ordering = "-threads_count"
        elif orderby == "comments":
            ordering = "-comments_count"

        return Magazine.objects.all().order_by(ordering)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="orderby",
                in_=openapi.IN_QUERY,
                description="Order magazines by 'threads_count', 'comments_count', or 'subscriptions_count'",
                type=openapi.TYPE_STRING,
                default="subscriptions_count",
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    


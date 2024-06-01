from django.views.generic import CreateView, UpdateView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from .forms import UserMultiForm, UserCreationMultiForm, profileForm
from django.contrib.auth import get_user_model

from django.views import View
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework.views import APIView
from .serializers import UserSerializer,EditUserSerializer, EditProfileSerializer, ProfileDetailSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from rest_framework import permissions
from django.shortcuts import redirect
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.views.generic.edit import UpdateView
from perfil import views as ProfileViews

@method_decorator(csrf_protect, name='dispatch')
class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        # Redireccionar a donde desees después del logout
        return redirect("thread_list")

# Create your views here.
def ProfileView(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, "profile.html", {"owner": user})




@require_http_methods(["DELETE", "POST"])
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return redirect('/')

def myProfile(request):
    if request.user.username:
        current_user = request.user
        return render(request, "myProfile.html", {"owner": request.user, "user":request.user})
    else:
        return redirect('/login')
    
def login(request):
    if request.user.is_authenticated:
        return redirect('thread_list')
    else:
        return render(request, "login.html")
User = get_user_model()

class UserSignupView(CreateView):
    form_class = UserCreationMultiForm
    success_url = reverse_lazy('thread_list')

    def form_valid(self, form):
        user = form['user'].save()
        profile = form['profile'].save(commit=False)
        profile.user = user
        profile.save()
        return redirect(self.get_success_url())

class EditUserView(UpdateView):
    model = User
    template_name = "editProfile.html"

    success_url = "/"
    form_class = UserMultiForm
    context_object_name = "owner"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(instance={
            'user': self.object,
            'profile': self.object.profile,
        })
        self.success_url = "/profile/"+str(self.request.user.id)+"/"
        return kwargs
    
    def form_valid(self, form):
        user_form = form['user']
        profile_form = form['profile']

        if user_form.is_valid() and profile_form.is_valid():
            
            user = user_form.save()

            profile = profile_form.save(commit=False)
            profile.save()

            

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('myProfile', kwargs={'pk': self.request.user.pk})


class EditUserAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'user': {
                                    'type': 'object',
                                    'properties': {                                       
                                        'username': {'type': 'string'}
                                    }
                                },
                                'profile': {
                                    'type': 'object',
                                    'properties': {                                       
                                        'bio': {'type': 'string'}
                                    }
                                }
                            }),
                     responses={200: openapi.Response('Success', ProfileDetailSerializer), 401: openapi.Response("detail: Authentication credentials were not provided."), 403: openapi.Response("detail: Authentication credentials do not match.")},
                     operation_summary='Update user profile',
                     operation_description='Update user profile information (text only).',
                     
                )    
    def put(self, request, user_id):
        if(not request.user.id == user_id):
          return Response({"detail: Authentication credentials do not match."}, status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, id=user_id)
        user_serializer = EditUserSerializer(user, data=request.data.get('user'))
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        profile_serializer = EditProfileSerializer(user.profile, data=request.data.get('profile'))
        if profile_serializer.is_valid():
            profile_serializer.save()
        else:
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(ProfileViews.get_details(request, user_id))
        
    
@permission_classes((permissions.AllowAny,))
class UploadImages(APIView):
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
                    request_body=None,
                    manual_parameters=[  # Add manual parameters for file upload and user/profile data
                        openapi.Parameter(
                            'avatar', openapi.IN_FORM, 
                            description="Avatar to upload", 
                            type=openapi.TYPE_FILE
                        ),
                        openapi.Parameter(
                            'cover', openapi.IN_FORM, 
                            description="Cover to upload", 
                            type=openapi.TYPE_FILE
                        )
                     ],
                     responses={200: openapi.Response('Success', ProfileDetailSerializer), 401: openapi.Response("detail: Authentication credentials do not match.")},
                     operation_summary='Update user profile',
                     operation_description='Update user profile information (text only).',
                     
                )     
    def put(self, request, user_id):        
        if(not request.user.id == user_id):
          return Response({"detail: Authentication credentials do not match."}, status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, id=user_id)
        profile = user.profile
        if(request.data.get('avatar')):
          profile.avatar = request.data.get('avatar')
        if(request.data.get('cover')):
          profile.cover = request.data.get('cover')
        profile_serializer = EditProfileSerializer(profile, data=request.data, partial = True)
        if profile_serializer.is_valid():
            profile_serializer.save()
        else:
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(ProfileViews.get_details(request, user_id))


def image_view(request):

    if request.method == 'POST':
        form = profileForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = profileForm()
    

def google_login(request):
    return redirect('/accounts/google/login')
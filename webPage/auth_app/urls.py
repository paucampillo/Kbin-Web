from urllib import request
from django.urls import path,include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from . import views
from django.conf.urls.static import static
from django.conf import settings

from .views import CustomLogoutView
#from ..webPage import settings

urlpatterns = [
    path('login/', views.login, name="login"),

    path('profile/<int:pk>/edit', views.EditUserView.as_view(), name="myProfile"),
    path('api/profile/<int:user_id>/edit/', views.EditUserAPIView.as_view(), name="myProfileApi"),
    path('api/profile/<int:user_id>/edit/images/', views.UploadImages.as_view(), name="myProfileApiImages"),
    path('accounts/', include('allauth.urls'), name="accounts"),
    #path('accounts/google/login/', views.loginRedirect, name="redirect"),
    path('logout', CustomLogoutView.as_view(), name='logout'),
    path("profile/<int:pk>/delete", views.delete_user, name="profile_delete"),
    path('google-login/', views.google_login, name='google_login'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
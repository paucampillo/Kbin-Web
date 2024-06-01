
from django.urls import path

from . import views
from .apis import UserThreadsView,UserCommentsView,UserBoostsView,UserInfoView

urlpatterns = [
    path('profile/<int:user_id>/', views.profile_detail, name='profile_detail'),
    path('api/profile/<int:user_id>/', views.profile_detail_api, name='profile_detail_api'),
    path('api/profile/myprofile/', views.my_profile_detail_api, name='my_profile_api'),
    path('profile/<int:user_id>/threads', views.profile_detail, name='profile_threads'),
    path('profile/<int:user_id>/comments', views.profile_detail, name='profile_comments'),
    path('profile/<int:user_id>/boosts', views.profile_detail, name='profile_boosts'),
    
]

urlpatterns += [
    path('api/profile/<int:user_id>/threads/', UserThreadsView.as_view(), name='user-threads-api'),
    path('api/profile/<int:user_id>/comments/', UserCommentsView.as_view(), name='user-comments-api'),
    path('api/profile/<int:user_id>/boosts/', UserBoostsView.as_view(), name='user-boosts-api'),
    path('api/profile/<int:user_id>/info/', UserInfoView.as_view(), name='user-info-api'),
]
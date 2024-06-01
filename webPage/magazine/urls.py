"""
This file contains the URL patterns for the magazine app.
"""

from django.urls import path

from . import views

from .apis import MagazineList,MagazineSubscriptionView,MagazineThreadsView,MagazineDetailView

urlpatterns = [
    path("newMagazine/", views.create_magazine, name="newMagazine"),
    path("magazines/", views.magazines, name="magazines"),
    path(
        "subscribe/<int:magazine_id>/",
        views.subscribe_to_magazine,
        name="subscribe_to_magazine",
    ),
    path(
        "unsubscribe/<int:magazine_id>/",
        views.unsubscribe_from_magazine,
        name="unsubscribe_from_magazine",
    ),
]

urlpatterns += [
    path('api/magazines/', MagazineList.as_view(), name='api-magazines'),
    path('api/magazines/<int:magazine_id>/subscriptions/', MagazineSubscriptionView.as_view(), name='magazine-subscriptions'),
    path('api/magazines/<int:magazine_id>/', MagazineDetailView.as_view(), name='magazine-detail'),
    path('api/magazines/<int:magazine_id>/threads/', MagazineThreadsView.as_view(), name='magazine-threads'),


]

"""
URL configuration for webPage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from threads import urls as urlThreads
from magazine import urls as urlMagazine
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="Kbin API",
        default_version="v1",
        description="This is the Open API documentation for the REST API of our beloved application Wall of Tweets deployed at https://djangokbin.fly.dev/."
        + "<br> All operations are executable. <br> All the POST, PUT and DELETE operations requires authentication. In this case, you must Authorize your request by providing the token value"
        + "that appears at your profile page. <br> The token must be provided in the format `Token <your_token>`. The token must be provided in the header of the request",
    ),
    public=True,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(urlThreads)),
    path("", include("auth_app.urls")),
    path("", include(urlMagazine)),
    path("", include("perfil.urls")),
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("api-auth/", include("rest_framework.urls")),
]

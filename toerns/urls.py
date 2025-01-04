"""
---------------------------------------------------------------------
toerns URL Configuration

in pythonanywhere Bash console:
git pull git@github.com:volkerpetersen/DjangoWebsites.git
---------------------------------------------------------------------

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.urls import path, re_path
from django.conf import settings
from . import views
from toerns.models import toerndirectory

handler404 = 'toerns.views.error_404'
handler500 = 'toerns.views.error_500'

urlpatterns = [
    re_path(r"^$", views.index, name="Directory"),
    re_path(r"^gallery/", views.gallery, name="Gallery"),
    re_path(r"^dashboard/", views.dashboard, name="Dashboard"),
    re_path(r"^safetyAndreas/", views.safetyAndreas, name="Safety-Andreas"),
    re_path(r"^weather/", views.weather, name="Weather"),
    path("plotRoute/<routeName>", views.plotRoute, name="Route"),
    path("admin/", admin.site.urls),  # Django Admin site),
]

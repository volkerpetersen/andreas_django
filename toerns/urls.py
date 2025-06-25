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
    path("gallery", views.gallery, name="Gallery"),
    path("dashboard", views.dashboard, name="Dashboard"),
    path("safetyAndreas", views.safetyAndreas, name="Safety"),
    path("updateTrip", views.updateTrip, name="Update-Trip"),
    path("navTools", views.navTools, name="Nav Tools"),
    path("documentation", views.documentation, name="Documentation"),
    path("weather", views.weather, name="Weather"),
    path("admin", admin.site.urls, name="Admin-Page"),  # Django Admin site),
    path("printDirectory", views.printDirectory, name="PrintDirectory"),
    # helper URL, not directly accessible for the user
    path("updateTripData", views.updateTripData, name="updateTripData"),
    path("navToolsData", views.navToolsData, name="navToolsData"),
    path("plotRoute/<routeName>", views.plotRoute, name="Route"),
]

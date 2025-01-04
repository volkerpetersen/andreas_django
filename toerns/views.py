# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------
toerns Views definitions

in pythonanywhere Bash console:
git pull git@github.com:volkerpetersen/toerns_django.git

site admin page /admin: petersen toerns
---------------------------------------------------------------------
"""

import json
import os
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core import serializers
from django.conf import settings as conf_settings
from django.http import JsonResponse
from toerns.models import toerndirectory, fetchRouteData
from toerns.settings import SQLITE

def fetchContent(route="all"):
    """---------------------------------------------------------------------
        function to create a dictionary with data to be passed into a
        html file

        Args:
            route (str): route option are:
                None
                all
                specific route only (specified by route name)

        Return:
            content (dictionary): dictonary holding the data
    """

    dateTimeStr = '%Y-%m-%d %H:%M:%S'
    
    dateStr = datetime.now().strftime(dateTimeStr)
    css = "../static/css/SailingLog.css?v=" + dateStr
    js = "../static/js/SailingLog.js?v=" + dateStr

    content = {
        "css": css,
        "js": js,
        "today": datetime.now(),
    }

    if route == "all":
        #trips = toerndirectory.objects.filter(
        #    startDate__lte=datetime.now()).order_by("-startDate")
        trips = toerndirectory.objects.all().order_by("-startDate")
        if trips is None:
            trips = {}
    elif route == "sqlfiles":
        query = toerndirectory.objects.all().values("maptable")
        trips = {}
        idx = 0
        for q in query:
            trips[q['maptable']+".sql"] = idx
            idx += 1
    elif route is None:
        trips = {}
    else:
        trips = toerndirectory.objects.filter(maptable=route)
        if trips is None:
            trips = {}

    content["trips"] = trips
    if route != "sqlfiles":
        # if trips is a dictionary, don't serialize it
        content["tripsJSON"] = json.dumps(serializers.serialize("json", trips))

    #print(f"{len(trips)} trips in SqLite")
    return content


def index(request):
    """---------------------------------------------------------------------
        view function for the home page with the Toern Directory
    """
    return render(request, "toerns/index.html", context=fetchContent(route="all"))


def gallery(request):
    """---------------------------------------------------------------------
        view function for the Gallery page
    """
    return render(request, "toerns/gallery.html", context=fetchContent(route="all"))


def dashboard(request):
    """---------------------------------------------------------------------
        view function for the Dashboard page
    """
    return render(request, "toerns/dashboard.html", context=fetchContent(route="all"))


def safetyAndreas(request):
    """---------------------------------------------------------------------
        view function for the Andreas Safety page
    """
    return render(request, "toerns/safetyAndreas.html", context=fetchContent(route=None))

def safetyZigzag(request):
    """---------------------------------------------------------------------
        view function for the Zigzag Safety page
    """
    return render(request, "toerns/safetyZigzag.html", context=fetchContent(route=None))


def weather(request):
    """---------------------------------------------------------------------
        view function for the Weather page
    """
    return render(request, "toerns/weather.html", context=fetchContent(route=None))

def ais(request):
    """---------------------------------------------------------------------
        view function for the AIS display
    """
    return render(request, "toerns/ais.html", context=fetchContent(route=None))


def navigation(request):
    """---------------------------------------------------------------------
        Compute the Rhumb Line and Great Circle Distance between 2 points
    """
    return render(request, "toerns/navigation.html", context=fetchContent(route=None))


def printDirectory(request):
    """---------------------------------------------------------------------
        view function for the print version of Toern Directory
    """
    return render(request, "toerns/printDirectory.html", context=fetchContent(route="all"))


@ csrf_exempt
def upload_sqlite(request):
    """---------------------------------------------------------------------
        ajax function to execute an SQLite query
    """
    import sqlite3

    sqlFile = request.POST.get("sqlFile", None)
    path = conf_settings.STATICFILES_DIRS[0]
    filename = os.path.normpath(os.path.join(path, "sqlite_files/" + sqlFile))

    response = {"status": "success",
                "msg": "Updated the SQLite table '%s'" % sqlFile}

    # fetch the SQLite query and process it
    try:
        with open(filename, "r") as file:
            sqliteQuery = file.read()
    except:
        response["status"] = "error"
        response["msg"] = "Error reading SQLite query file '%s'" % filename
        return JsonResponse(response)

    # execute the SQLite query and write data to SQLite DB
    try:
        db = sqlite3.connect(SQLITE)
        cursor = db.cursor()
        cursor.executescript(sqliteQuery)
        db.commit()
        db.close()
    except:
        response["status"] = "error"
        response["msg"] = "Error executing SQLite query '%s'" % sqlFile

    return JsonResponse(response)


def plotRoute(request, routeName):
    """---------------------------------------------------------------------
        view function to plot the route on a Google Map
    """

    dbTable = fetchRouteData(routeName)
    routeData = dbTable.objects.all()
    if routeData is None:
        routeData = {}

    content = fetchContent(route=routeName)
    content["routeName"] = routeName
    content["wps"] = routeData
    content["wpsJSON"] = json.dumps(serializers.serialize("json", routeData))

    return render(request, "toerns/plotRoute.html", content)


def update_sqliteDB(request):
    """---------------------------------------------------------------------
        view function update the sqlite DB
    """
    from django.db import connection

    content = fetchContent(route="all")
    for trip in content["trips"]:
        routeName = trip.maptable
        if len(routeName):
            #query = (f"ALTER TABLE '{routeName}' RENAME COLUMN 'to' TO 'name'")
            query = (f"ALTER TABLE '{routeName}' DROP COLUMN 'from'")
            print(query)
            with connection.cursor() as cursor:
                x=cursor.execute(query)
                print(x)

    return render(request, "toerns/index.html", content)

# add custom error pages
def error_404(request, exception=None):
    return render(request, 'errors/404.html', context={})

def error_500(request):
    return render(request, 'errors/500.html', context={})

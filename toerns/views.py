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
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.core import serializers
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.db import connection
from toerns.models import toerndirectory, fetchRouteData
from toerns.settings import SQLITE, MEDIA_ROOT
from toerns.NavToolsLib import NavTools


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

def updateTrip(request):
    """---------------------------------------------------------------------
        view function to gather user input for a route update request
    """
    content = fetchContent(route=None)
    content["trips"] = toerndirectory.objects.all().order_by("-startDate")
    return render(request, "toerns/updateTrip.html", context=content)

@require_POST
def updateTripData(request):
    """---------------------------------------------------------------------
        view function to process a route/image update AJAX request
    """
    content = {}
    content['msg'] = None
    msg = ""

    if request.FILES['fileUpload']:
        uploadedFile = request.FILES['fileUpload']
        fs = FileSystemStorage()
        filePath = os.path.normpath(os.path.join(os.path.join(MEDIA_ROOT,"routes"),uploadedFile.name))
        if fs.exists(filePath):
            fs.delete(filePath)
        filename = fs.save(filePath, uploadedFile)
        fileURL = fs.url(filename)
        fn = filename.split('.')
        routeName = fn[0]
        routeFormat = fn[1]
    else:
        content['success'] = False
        content['msg'] = F"No valid waypoint file received."
        return JsonResponse(content)

    if request.FILES['imageUpload']:
        uploadedFile = request.FILES['imageUpload']
        fs = FileSystemStorage()
        filePath = os.path.normpath(os.path.join(os.path.join(MEDIA_ROOT,"images"),uploadedFile.name))
        if fs.exists(filePath):
            fs.delete(filePath)
        imageName = fs.save(filePath, uploadedFile)
        imageURL = fs.url(imageName)
    else:
        content['success'] = False
        content['msg'] = F"No valid image file received."
        return JsonResponse(content)

    try:
        if not filename:
            content['success'] = False
            content['msg'] = f"Route name must be specified first in the 'Toerndirectory' table field 'maptable'."
            return JsonResponse(content)

        content['success'] = True
        navtools = NavTools()

        if routeFormat == "gpx":
            msg = navtools.parseSQLRouteFile(MEDIA_ROOT, MEDIA_ROOT, filename)
            filename = filename.replace('gpx', 'sql')

        (content['msg'], routeName) = uploadSQL(MEDIA_ROOT, filename)

        # get the current toern we're working with
        startDate = request.POST['routeSelect']
        #print(f"startDate: {startDate}")

        startDate = datetime.strptime(startDate, '%b. %d, %Y').strftime('%Y-%m-%d')
        #print(f"startDate: {startDate}")

        # update the maptable and image entries in the Toerndirectory table
        toern = toerndirectory.objects.get(startDate=startDate)
        toern.maptable = routeName
        toern.image = imageName
        toern.save()

        dbTable = fetchRouteData(routeName)
        numWaypoints = dbTable.objects.all().count()
        content['msg'] = F"Updated {numWaypoints} waypoints in DB table {routeName} and uploaded the trip image {imageName}."

    except Exception as e:
        content['success'] = False
        content['msg'] = F"Failed to update the image and/or route data to database.<br>{str(e)}"
    return JsonResponse(content)

def uploadSQL(pathName, fileName):
    """---------------------------------------------------------------------
        view function to upload an sql file to the Sqlite DB
    """
    routeName = None
    try:
        fn = os.path.normpath(os.path.join(pathName, fileName))
        
        with open(fn, 'r') as sql_file:
            sql_content = sql_file.read()
        
        with connection.cursor() as cursor:
            for command in sql_content.split(';'):
                command = command.strip()
                if command:
                    cursor.execute(command)
                    if "INSERT OR REPLACE INTO" in command:
                        routeName = command.replace('INSERT OR REPLACE INTO "', "")
                        routeName = routeName.split('"')
                        routeName = routeName[0]

        msg = "File successfully added to the database."    
    except Exception as e:
        msg = (f"DB error: {str(e)}")
        print(msg)

    return (msg, routeName)


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

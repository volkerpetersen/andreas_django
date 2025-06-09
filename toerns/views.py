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
import csv
import io
import base64
from datetime import datetime
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.core import serializers
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.db import connection
from django.db.models import Sum
from django_user_agents.utils import get_user_agent
from toerns.models import toerndirectory, fetchRouteData
from toerns.settings import MEDIA_ROOT, DEBUG
from toerns.NavToolsLib import NavTools
import matplotlib
matplotlib.use('SVG')  # 'Agg' or 'SVG'
import matplotlib.pyplot as plt
import pandas as pd

dateFmtRead = ["%B %d, %Y",     # April 07, 2025
               "%b. %d, %Y",    # Apr. 07, 2025
               "%b %d, %Y",     # Apr 07, 2025
]
dateFmtWrite = "%Y-%m-%d"     # 2025-04-07

gpx_header = """<?xml version="1.0" encoding="utf-8" ?>
<gpx version="1.1" creator="OpenCPN" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" xmlns:opencpn="http://www.opencpn.org">
<rte>
<name>Route Name</name>
<extensions>
    <opencpn:start></opencpn:start>
    <opencpn:end></opencpn:end>
    <opencpn:viz>1</opencpn:viz>
    <opencpn:guid>17ab0000-eb25-48bc-930a-000000000000</opencpn:guid>
</extensions>\n"""


def fetchContent(request, route="all"):
    """---------------------------------------------------------------------
        function to create a dictionary with data to be passed into a
        html file

        Args:
            request (obj): request object
            route (str): route option are:
                None
                all
                specific route only (specified by route name)

        Return:
            content (dictionary): dictonary holding the data
    """

    dateTimeStr = f"{dateFmtWrite} %H:%M:%S"
    
    dateStr = datetime.now().strftime(dateTimeStr)
    css = "../static/css/SailingLog.css?v=" + dateStr
    js = "../static/js/SailingLog.js?v=" + dateStr

    user_agent = get_user_agent(request)
    content = {
        "css": css,
        "js": js,
        "today": datetime.now(),
        'is_mobile': user_agent.is_mobile,
        'is_tablet': user_agent.is_tablet,
        'is_desktop': not user_agent.is_mobile,
    }
    #print(f"is_mobile: {content['is_mobile']}")

    if route == "all":
        if DEBUG:
            trips = toerndirectory.objects.all().order_by("-startDate")
        else:
            today = datetime.now().strftime(dateFmtWrite)
            trips = toerndirectory.objects.filter(startDate__lte=today).order_by("-startDate")
        
        if trips is None:
            trips = {}
            content["numToerns"] = 0
            content["sumMiles"] = 0
        else:
            content["numToerns"] = trips.count()
            content["sumMiles"] = trips.aggregate(Sum('miles'))['miles__sum']

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

    #print(f"{len(trips)} trips in SqLite")
    return content


def index(request):
    """---------------------------------------------------------------------
        view function for the home page with the Toern Directory
    """
    return render(request, "toerns/index.html", 
                  context=fetchContent(request, route="all"))


def gallery(request):
    """---------------------------------------------------------------------
        view function for the Gallery page
    """
    return render(request, "toerns/gallery.html", 
                  context=fetchContent(request, route="all"))


def dashboard(request):
    """---------------------------------------------------------------------
        view function for the Dashboard page
    """
    content = fetchContent(request, route="all")
    trips = content['trips']
    destinationMiles = {}
    destinationCount = {}
    skipperMiles = {}
    crewStats = {}
    annualMiles = {}
    annualDays = {}
    for trip in trips:
        try:
            miles = float(trip.miles)
            daysAtSea = int(trip.daysAtSea)
        except:
            miles = 0
            daysAtSea = 0
        year = trip.startDate.strftime("%Y")
        skipper = trip.skipper.first()
        name = f"{skipper.firstName} {skipper.lastName}"
        #name = name.replace("&uuml;", "ue");
        #name = name.replace("&auml;", "ae");
        #name = name.replace("&ouml;", "oe");

        if trip.georegion in destinationMiles:
            destinationMiles[trip.georegion] += miles
        else:
            destinationMiles[trip.georegion] = miles

        if trip.georegion in destinationCount:
            destinationCount[trip.georegion] += 1
        else:
            destinationCount[trip.georegion] = 1
        
        if name in skipperMiles:
            skipperMiles[name] += miles
        else:
            skipperMiles[name] = miles

        if year in annualMiles:
            annualMiles[year] += miles
        else:
            annualMiles[year] = miles

        if year in annualDays:
            annualDays[year] += trip.daysAtSea
        else:
            annualDays[year] = trip.daysAtSea

        for crew in trip.crew.all():
            name = f"{crew.firstName} {crew.lastName}"
            if name in crewStats:
                crewStats[name]['miles'] += miles
                crewStats[name]['days'] += daysAtSea
                crewStats[name]['trips'] += 1
                if 'Skipper' in crewStats[name]['role']:
                    crewStats[name]['role'] = 'Skipper and Crew'
            else:
                crewStats[name] = {'miles': miles, 'days': daysAtSea, 'trips': 1, 'role': 'Crew'}

        for skipper in trip.skipper.all():
            name = f"{skipper.firstName} {skipper.lastName}"
            if name in crewStats:
                crewStats[name]['miles'] += miles
                crewStats[name]['days'] += daysAtSea
                crewStats[name]['trips'] += 1
                if 'Crew' in crewStats[name]['role']:
                    crewStats[name]['role'] = 'Skipper and Crew'
            else:
                crewStats[name] = {'miles': miles, 'days': daysAtSea, 'trips': 1, 'role': 'Skipper'}

    content['destinationMiles'] = destinationMiles
    content['destinationCount'] = destinationCount
    content['skipperMiles'] = skipperMiles
    content['annualMiles'] = annualMiles
    content['annualDays'] = annualDays
    content['crewStats'] = crewStats.items()

    return render(request, "toerns/dashboard.html", 
                  context=content)


def documentation(request):
    """---------------------------------------------------------------------
        view function for the Documentation page
    """
    return render(request, "toerns/documentation.html", 
                  context=fetchContent(request, route=None))

def safetyAndreas(request):
    """---------------------------------------------------------------------
        view function for the Andreas Safety page
    """
    return render(request, "toerns/safetyAndreas.html", 
                  context=fetchContent(request, route=None))

def updateTrip(request):
    """---------------------------------------------------------------------
        view function to gather user input for a route update request
    """
    content = fetchContent(request, route=None)
    content["trips"] = toerndirectory.objects.all().order_by("-startDate")
    return render(request, "toerns/updateTrip.html", context=content)

@require_POST
def updateTripData(request):
    """---------------------------------------------------------------------
        AJAX function to process a route/image update AJAX request
    """
    content = {}
    content['msg'] = ""

    try:
        # get the current toern we're working with
        startDate = request.POST['routeSelect']
        startDate = parseDateString(startDate)
        #print(f"startDate: {startDate}")
    except:
        content['msg'] = F"No valid trip selected."
        return JsonResponse(content)

    if 'true' in request.POST['route']:
        content['successRoute'] = True
        content['successImage'] = False
        uploadedFile = request.FILES.get('routeUpload')
        if uploadedFile:
            fs = FileSystemStorage()
            filePath = os.path.normpath(os.path.join(os.path.join(MEDIA_ROOT,"routes"),uploadedFile.name))
            if fs.exists(filePath):
                fs.delete(filePath)
            fileName = fs.save(filePath, uploadedFile)
            if not fileName:
                content['successRoute'] = False
                content['msg'] += f"Route file '{uploadedFile}' upload failed."
                return JsonResponse(content)
            fn = fileName.split('/').pop()
            fn = fn.split('.')
            routeName = fn[0]
            routeFormat = fn[1]

            try:
                navTools = NavTools()
                path = os.path.normpath(os.path.join(MEDIA_ROOT, 'routes'))
                if routeFormat.lower() == "gpx":
                    msg = navTools.parseSQLRouteFile(path, path, routeName)
                    #print(msg)
                    fileName = fileName.replace('gpx', 'sql')

                (msg, fn) = uploadSQL(MEDIA_ROOT, fileName)

                # update the maptable and image entries in the Toerndirectory table
                toern = toerndirectory.objects.get(startDate=startDate)
                toern.maptable = routeName
                toern.save()

                dbTable = fetchRouteData(routeName)
                numWaypoints = dbTable.objects.all().count()
                content['successRoute'] = True
                content['msg'] += F"Updated {numWaypoints} waypoints in DB table '{routeName}'."

            except Exception as e:
                content['successRoute'] = False
                content['msg'] += F"Failed to update the route data in the database.<br>{str(e)}"
        else:
            content['success'] = False
            content['msg'] += F"No valid waypoint file received."


    if 'true' in request.POST['image']:
        uploadedFile = request.FILES.get('imageUpload')
        if uploadedFile:
            fs = FileSystemStorage()
            filePath = os.path.normpath(os.path.join(os.path.join(MEDIA_ROOT,"images"),uploadedFile.name))
            if fs.exists(filePath):
                fs.delete(filePath)
            imageName = fs.save(filePath, uploadedFile)
            imageURL = fs.url(imageName)

            # update the maptable and image entries in the Toerndirectory table
            toern = toerndirectory.objects.get(startDate=startDate)
            toern.image = imageName
            toern.save()
            content['successImage'] = True
            content['msg'] += f"<br>Uploaded the image '{imageName}' to the website."
        else:
            content['successImage'] = False
            content['msg'] += F"<br>No valid image file received."

    return JsonResponse(content)

def parseDateString(dateString):
    """---------------------------------------------------------------------
        helper function to convert a date string into a standardized format
    """
    for fmt in dateFmtRead:
        try:
            date = datetime.strptime(dateString, fmt)
            return date.strftime(dateFmtWrite)
        except:
            pass
    return None
    
def navTools(request):
    """---------------------------------------------------------------------
        view function to provide some Navigation Tools
    """
    content = fetchContent(request, route=None)
    content["trips"] = toerndirectory.objects.all().order_by("-startDate")
    return render(request, "toerns/navTools.html", context=content)


@require_POST
def navToolsData(request):
    """---------------------------------------------------------------------
        AJAX function to process a navTools AJAX request
    """
    content = {}
    content['msg'] = None
    msg = ""

    try:
        navTools = NavTools()

        # handle Expedition weather routing analysis request
        if request.POST['weather'] == 'true':
            if request.FILES['weatherFileSelection'] and request.FILES['weatherFileSelection'].name.endswith('.csv'):
                csvFile = request.FILES['weatherFileSelection']
                decodedFile = csvFile.read().decode('utf-8').splitlines()
                data = csv.reader(decodedFile)
                records = []
                for row in data:
                    if len(row):
                        records.append(row)
            else:
                content['success'] = False
                content['msg'] = F"Invalid weather analysis file received."
                return JsonResponse(content)
        
            exp = navTools.Expedition_Weather_Routing_Analysis("", records, webpage=True)
            
            if len(exp):
                figs = plt.get_fignums()
                if len(figs):
                    figCtr = max(figs) + 1
                else:
                    figCtr = 1
                fig = plt.figure(figCtr, figsize=navTools.figsize)
                axs = fig.subplots(nrows=3, ncols=1, sharex=False)
                xlabel = f"Percentage of {exp['hours']:.2f} hrs race"
                
                # Page 1: first subplot - tws
                ax = axs[0]
                df = exp['df']

                navTools.plot_barh(df.sum(axis=1), ax=ax, 
                            title="TWS Distribution", ylabel="TWS (kts)")

                # Page 1: second subplot - twa
                ax = axs[1]
                twa_percent = df.sum(axis=0)
                navTools.plot_barh(twa_percent, ax=ax, 
                            title="TWA Distribution", ylabel="TWA (degrees)")

                # Page 1: third subplot - sails
                ax = axs[2]
                percent = [val / exp['hours'] for val in list(exp['sails'].values())]
                index = list(exp['sails'].keys())
                x = pd.DataFrame(data=percent, index=index)
                if('Total hours' in x.index):
                    x.drop(['Total hours'], inplace=True)
                navTools.plot_barh(x, ax=ax, title="Sail Utilization", ylabel="Sails")
                ax.set_xlabel(xlabel)

                buffer1 = io.BytesIO()
                fig.savefig(buffer1, format='png', bbox_inches="tight", pad_inches=0.25)
                buffer1.seek(0)
                plot1 = base64.b64encode(buffer1.getvalue()).decode('utf-8')
                buffer1.close()

                # Page 2: plot the TWA / TWD distribution
                figCtr = figCtr + 1
                fig = navTools.heat_map(exp, figCtr)
                buffer2 = io.BytesIO()
                fig.savefig(buffer2, format='png', bbox_inches="tight", pad_inches=0.3)
                buffer2.seek(0)
                plot2 = base64.b64encode(buffer2.getvalue()).decode('utf-8')
                buffer2.close()

                content['plot1'] = plot1
                content['plot2'] = plot2
                content['msg'] = ""
                content['file'] = csvFile.name
                content['success'] = True
            else:
                content['msg'] = "Error processing the Weather Routing data."
                content['success'] = False
        
            return JsonResponse(content)
        
        # handle SQL route analysis
        elif request.POST['sqlite'] == 'true':
            # prep AJAX request for analysis of a maptable in the SqLite DB
            startDateSQL = request.POST['routeSelect']
            startDate = parseDateString(startDateSQL)

            try:
                toern = toerndirectory.objects.get(startDate=startDate)
            except:
                msg = F"Can not find a trip record with startDate: {startDateSQL}"
                print(f"navToolsData(): {msg}")
                content['success'] = False
                content['msg'] = msg
                return JsonResponse(content)

            dbTable = fetchRouteData(toern.maptable)
            wps = dbTable.objects.all()

            # parse SQL route data and convert to GPX xml
            xml = gpx_header
            xml.replace("Route Name", toern.maptable)
            wp_ctr = 0
            for wp in wps:
                xml += '<rtept lat="' + str(wp.lat) + '" lon="' + str(wp.lon) + '">\n'
                xml += "<time></time>\n"
                xml += "<name>" + wp.name + "</name>\n"
                if wp.type == 'none':
                    xml += "<sym>empty</sym>\n"
                else:
                    xml += "<sym>"+ wp.type +"</sym>\n"

                if len(wp.notes):
                    xml += "<desc>"+wp.notes+"</desc>\n"

                xml += "<type>WPT</type>\n"
                xml += (
                    "<extensions><opencpn:guid>717ab0000-eb25-48bc-930a-%012d" % wp_ctr
                )
                xml += "</opencpn:guid>\n<opencpn:viz>0</opencpn:viz>\n<opencpn:viz_name>0</opencpn:viz_name>\n</extensions>\n</rtept>\n"
                wp_ctr += 1
            #print(f"\nconverted {wp_ctr} waypoints to xml string:\n{xml}\n")

        # handle .gpx route file analysis
        elif request.POST['route'] == 'true':
            # read xml data from GPX file
            if request.FILES['routeFileSelection']:
                specifiedFile = request.FILES['routeFileSelection']
                tripFile = specifiedFile.name
            else:
                content['success'] = False
                content['msg'] = F"No valid route file received."
                return JsonResponse(content)
        
            pathName = os.path.join(MEDIA_ROOT, "routes")
            fn = os.path.normpath(os.path.join(pathName, tripFile))

            with open(fn, 'r') as gpx_file:
                xml = gpx_file.read()

        # process XML data from either the SQL table of the GPX file
        if xml:
            colgroup = (F"<table><colgroup>"+
                        F"<col style='width: 30%;'>"+
                        F"<col style='width: 15%;'>"+
                        F"<col style='width: 15%;'>"+
                        F"<col style='width: 10%;'>"+
                        F"<col style='width: 10%;'>"+
                        F"<col style='width: 10%;'>"+
                        F"<col style='width: 10%;'>"+
                        F"</colgroup>"
            )
            msg = navTools.ComputeRouteDistances(xml, verbose=False, 
                    skipWP=False, noSpeed=False, tablefmt="html")
            msg = msg.replace("\nT", "<br>T")
            msg = msg.replace("\nAv", "<br>Av")
            msg = msg.replace("<table>", colgroup)
            content['success'] = True
            content['msg'] = msg
        else:
            content['success'] = False
            content['msg'] = F"Error processing gpx or SQL route data."

    except Exception as e:
        content['success'] = False
        content['msg'] = F"Failed to process the data.<br>{str(e)}"
    return JsonResponse(content)


def uploadSQL(pathName, fileName):
    """---------------------------------------------------------------------
        helper function to upload an sql file to the Sqlite DB
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
    return render(request, "toerns/weather.html", 
                  context=fetchContent(request, route=None))

def ais(request):
    """---------------------------------------------------------------------
        view function for the AIS display
    """
    return render(request, "toerns/ais.html", 
                  context=fetchContent(request, route=None))


def printDirectory(request):
    """---------------------------------------------------------------------
        view function for the print version of Toern Directory
    """
    return render(request, "toerns/printDirectory.html", 
                  context=fetchContent(request, route="all"))


def plotRoute(request, routeName):
    """---------------------------------------------------------------------
        view function to plot the route on a Google Map
        If no routeName is given or it is invalid redirect to Directory page 
    """

    try:
        if not table_exists(routeName):
            return redirect('Directory')
        dbTable = fetchRouteData(routeName)
        routeData = dbTable.objects.all()
    except Exception as e:
        print(f"\nDB table '{routeName}' does not exist.\nError: {str(e)}\n")
        return redirect('Directory')

    content = fetchContent(request, route=routeName)
    content["routeName"] = routeName
    content["wps"] = routeData
    content["wpsJSON"] = json.dumps(serializers.serialize("json", routeData))

    return render(request, "toerns/plotRoute.html", content)

def table_exists(table_name):
    return table_name in connection.introspection.table_names()


def plotRoute_redirect(request):
    """---------------------------------------------------------------------
        view function to predirect plotRoute when called w/o a routeName
    """
    return redirect('Directory')


def update_sqliteDB(request):
    """---------------------------------------------------------------------
        view function update the sqlite DB
    """
    from django.db import connection

    content = fetchContent(request, route="all")
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

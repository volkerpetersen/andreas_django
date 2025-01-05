"""
---------------------------------------------------------------------
toerns Models with the database definitions

https://pythonprogramming.net/django-web-development-python-tutorial/

in pythonanywhere Bash console:
git pull git@github.com:volkerpetersen/andreas_django.git
 
python manage shell ==> example 
  >>> from toerns.models import *
  >>> t = toerndirectory.objects.all()
---------------------------------------------------------------------
"""

from django.db import models

class toerndirectory(models.Model):
    """Define the Toern Directory Table"""

    startDate = models.DateField(primary_key=True,
                                 help_text="date in YYYY-MM-DD format")
    endDate = models.DateField(blank=True,
                               help_text="date in YYYY-MM-DD format")
    destination = models.CharField(blank=True, null=True, max_length=150)
    georegion = models.CharField(blank=True, null=True, max_length=40,
                                 help_text="Atlantic, Caribbean, Great Lakes, Pacific")
    maptable = models.CharField(blank=True, null=True, max_length=100,
                                help_text="name of the map table")
    boat = models.CharField(blank=True, null=True, max_length=400)
    miles = models.DecimalField(
        blank=True, null=True, max_digits=8, decimal_places=2)
    daysAtSea = models.IntegerField()
    skipper = models.CharField(blank=True, null=True, max_length=50)
    crew0 = models.CharField(blank=True, null=True, max_length=50)
    crew0 = models.CharField(blank=True, null=True, max_length=50)
    crew1 = models.CharField(blank=True, null=True, max_length=50)
    crew2 = models.CharField(blank=True, null=True, max_length=50)
    crew3 = models.CharField(blank=True, null=True, max_length=50)
    crew4 = models.CharField(blank=True, null=True, max_length=50)
    crew5 = models.CharField(blank=True, null=True, max_length=50)
    crew6 = models.CharField(blank=True, null=True, max_length=50)
    crew7 = models.CharField(blank=True, null=True, max_length=50)
    crew8 = models.CharField(blank=True, null=True, max_length=50)
    crew9 = models.CharField(blank=True, null=True, max_length=50)
    image = models.CharField(blank=True, null=True, max_length=100)
    picturelink = models.CharField(blank=True, null=True, max_length=200)

    class Meta:
        managed = True
        db_table = "ToernDirectoryTable"

    def __str__(self):
        return f"{self.startDate}: {self.destination}"

class Races(models.Model):
    """Define the Race """
    raceDate = models.DateField(primary_key=True,
                                help_text="date in YYYY-MM-DD format")
    raceName = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = "Races"

    def __str__(self):
        return f"{self.raceDate}: {self.raceName}"

class Participant_Tracking(models.Model):
    """Table to track race participants ToDos"""
    id = models.IntegerField(primary_key=True)
    raceDate = models.ForeignKey(
        Races, on_delete=models.CASCADE, help_text="Lookup from the 'Races' table")
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    signupDate = models.DateField(help_text="date in YYYY-MM-DD format")
    reviewDate = models.DateField(help_text="date in YYYY-MM-DD format")

    class Meta:
        managed = True
        db_table = "Participant_Tracking"

    def __str__(self):
        return f"Race {self.raceID}: {self.firstName} {self.lastName}"

def fetchRouteData(tableName):
    class RouteMetaClass(models.base.ModelBase):
        def __new__(cls, name, bases, attrs):
            name += tableName
            return models.base.ModelBase.__new__(cls, name, bases, attrs)

    class RouteData(models.Model):
        __metaclass__ = RouteMetaClass

        id = models.AutoField(primary_key=True)
        name = models.TextField(db_column="name", blank=True, null=True)
        lat = models.TextField(blank=True, null=True)
        lon = models.TextField(blank=True, null=True)
        type = models.TextField(blank=True, null=True)
        image = models.TextField(blank=True, null=True)
        notes = models.CharField(max_length=80, blank=True, null=True)

        class Meta:
            db_table = tableName

    return RouteData


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

class SailingSkills(models.Model):
    """Table with approved crew sailing skills (navigator, skipper, trimmmer, main, etc.)"""
    skill = models.CharField(max_length=20)

    class Meta:
        managed = True
        db_table = "SailingSkills"
        verbose_name_plural = 'SailingSkills'
        ordering = ['skill']

    def __str__(self):
        return f"{self.skill}"

class CrewMembers(models.Model):
    """Table to track of the crew members"""
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    email = models.CharField(max_length=50, blank=True)
    skills = models.ManyToManyField(SailingSkills, blank=True)

    class Meta:
        managed = True
        db_table = "CrewMembers"
        verbose_name_plural = 'Crew Members'
        ordering = ['lastName', 'firstName']

    def __str__(self):
        return f"{self.firstName} {self.lastName}"

class toerndirectory(models.Model):
    """Define the Toern Directory Table"""

    geoChoices = (
        ('Atlantic', u'Atlantic'),
        ('Baltic', u'Baltic'),
        ('Caribbean', u'Caribbean'),
        ('Coratia', u'Croatia'),
        ('Great Lakes', u'Great Lakes'),
        ('Pacific', u'Pacific')
    )

    id = models.AutoField(primary_key=True)
    startDate = models.DateField(help_text="date in YYYY-MM-DD format")
    endDate = models.DateField(help_text="date in YYYY-MM-DD format")
    destination = models.CharField(blank=True, null=True, max_length=150)
    georegion = models.CharField(blank=True, null=True, max_length=40, choices=geoChoices,
                                 help_text="Atlantic, Baltic, Caribbean, Croatia, Great Lakes, Pacific")
    maptable = models.CharField(blank=True, null=True, max_length=100,
                                help_text="name of the Google Maps waypoints table")
    boat = models.CharField(blank=True, null=True, max_length=810)
    miles = models.DecimalField(null=True, max_digits=8, decimal_places=2)
    daysAtSea = models.IntegerField()
    skipper = models.ManyToManyField(CrewMembers, blank=True, related_name='skipperToern')
    crew = models.ManyToManyField(CrewMembers, blank=True, related_name='crewToern')
    image = models.CharField(blank=True, null=True, max_length=100)
    picturelink = models.CharField(blank=True, null=True, max_length=200)

    class Meta:
        managed = True
        db_table = "ToernDirectory"
        verbose_name_plural = 'Toern Directory'

    def __str__(self):
        return f"{self.startDate}: {self.destination}"

_model_cache = {}

def fetchRouteData(table_name):
    # Return cached model if exists
    if table_name in _model_cache:
        return _model_cache[table_name]
    
    # Define model fields
    class Meta:
        db_table = table_name
        managed = False  # Critical for dynamic tables
    
    # Create model class dynamically
    attrs = {
        'id': models.AutoField(primary_key=True),
        'name': models.TextField(blank=True, null=True),
        'lat': models.FloatField(blank=True, null=True),
        'lon': models.FloatField(blank=True, null=True),
        'type': models.TextField(blank=True, null=True),
        'image': models.TextField(blank=True, null=True),
        'notes': models.CharField(max_length=80, blank=True, null=True),
        'Meta': Meta,
        '__module__': __name__
    }
    
    # Create and cache model
    model_class = type(f'RouteData_{table_name}', (models.Model,), attrs)
    _model_cache[table_name] = model_class
    return model_class

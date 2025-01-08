from django.contrib import admin
from .models import toerndirectory

class toerndirectoryAdmin(admin.ModelAdmin):
    # Create your own display
    list_display = ("startDate", "destination", "miles")
    list_filter = ("georegion", )
    search_fields = ("skipper", )


# Register your models here that you want to give Admin access to
admin.site.register(toerndirectory, toerndirectoryAdmin)

admin.site.site_header = "Toern Administration"


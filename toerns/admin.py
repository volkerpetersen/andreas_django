from django.contrib import admin
from .models import toerndirectory
from .models import CrewMembers
from django import forms

class toerndirectoryForm(forms.ModelForm):
    class Meta:
        model = toerndirectory
        fields = '__all__'
        widgets = {
            'boat': forms.Textarea(attrs={'rows': 8, 'cols': 45}),
        }

class toerndirectoryAdmin(admin.ModelAdmin):
    filter_horizontal = ('skipper', 'crew')
    # Create your own display
    list_display = ("startDate", "destination", "miles")
    list_filter = ("georegion", )
    search_fields = ("skipper", )
    form = toerndirectoryForm


class crewMemberAdmin(admin.ModelAdmin):
    # Create your own display
    list_display = ("firstName", "lastName", 'get_skills')
    search_fields = ("lastName", )

    def get_skills(self, obj):
        # Retrieve and join all related skills into a single string
        return ", ".join(sorted(skill.skill for skill in obj.skills.all()))

    get_skills.short_description = 'Skills'  # Column name in the admin interface

# Register your models here that you want to give Admin access to
admin.site.register(toerndirectory, toerndirectoryAdmin)
admin.site.register(CrewMembers, crewMemberAdmin)

admin.site.site_header = "Toern Administration"


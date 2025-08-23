from django.contrib import admin
from .models import toerndirectory
from .models import CrewMembers
from .models import SailingSkills
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
    list_display = ("startDate", "destination", "miles", "daysAtSea")
    list_filter = ("georegion", )
    ordering = ["-startDate"]
    form = toerndirectoryForm


class sailingSkillAdmin(admin.ModelAdmin):
    list_display = ("skill", )
    ordering = ["skill", ]


class crewMemberAdmin(admin.ModelAdmin):
    # Create your own display
    list_display = ("firstName", "lastName", 'get_skills')
    search_fields = ("lastName", )
    ordering = ["lastName", "firstName", ]

    def get_skills(self, obj):
        # Retrieve and join all related skills into a single string
        return ", ".join(sorted(skill.skill for skill in obj.skills.all()))

    get_skills.short_description = 'Skills'  # Column name in the admin interface

# Register your models here that you want to give Admin access to
# table SailingSkills is managed and can be set indirectly thru Crew table
admin.site.register(toerndirectory, toerndirectoryAdmin)
admin.site.register(CrewMembers, crewMemberAdmin)
admin.site.register(SailingSkills, sailingSkillAdmin)
admin.site.site_header = "Toern Administration"

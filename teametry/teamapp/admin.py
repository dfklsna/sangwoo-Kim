from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Team, Participant, SurveyResponse

admin.site.register(Team)
admin.site.register(Participant)
admin.site.register(SurveyResponse)

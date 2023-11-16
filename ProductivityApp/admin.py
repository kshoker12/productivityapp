from django.contrib import admin
from .models import Coordinator, Week, CurrentWeek

admin.site.register(Coordinator)
admin.site.register(Week)
admin.site.register(CurrentWeek)
from django.contrib import admin
from .models import Coordinator, Week, CurrentWeek, AppState, Files

admin.site.register(Coordinator)
admin.site.register(Week)
admin.site.register(CurrentWeek)
admin.site.register(AppState)
admin.site.register(Files)
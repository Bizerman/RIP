from django.contrib import admin

from .models import Gateway_el
from .models import Gateway_mission

admin.site.register(Gateway_el)
admin.site.register(Gateway_mission)

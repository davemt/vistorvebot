from telepresence.robotarmy.models import Robot
from django.contrib import admin

class RobotAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'state', 'ip',)
    readonly_fields = ('last_heartbeat',)
    list_filter = ('state',)

admin.site.register(Robot, RobotAdmin)

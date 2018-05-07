from django.contrib import admin
from .models import Alarm, AlarmLog

# Register your models here.
#class AlarmAdmin(admin.ModelAdmin):
#    fields = ['text', 'repeat']
class AlarmLogAdmin(admin.ModelAdmin):
    actions = None
admin.site.register(Alarm)#, AlarmAdmin)
#admin.site.disable_action('delete_selected')
admin.site.register(AlarmLog, AlarmLogAdmin)
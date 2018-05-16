from django.contrib import admin
from .models import Log,Machine

# Register your models here.
class LogAdmin(admin.ModelAdmin):
    pass
class MachineAdmin(admin.ModelAdmin):
    pass
admin.site.register(Log,LogAdmin)
admin.site.register(Machine,MachineAdmin)
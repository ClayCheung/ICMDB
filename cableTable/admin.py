from django.contrib import admin
from cableTable import models
# Register your models here.

admin.site.register(models.Locate)
admin.site.register(models.Project)
admin.site.register(models.Asset)
admin.site.register(models.Server)
admin.site.register(models.NetworkDevice)
admin.site.register(models.Port)

admin.site.register(models.CableTableFille)

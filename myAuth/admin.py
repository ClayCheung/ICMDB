from django.contrib import admin
from myAuth import models
# Register your models here.

admin.site.register(models.Role)
admin.site.register(models.UserInfo)
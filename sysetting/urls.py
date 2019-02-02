from django.urls import path
from sysetting import views

app_name = 'sysetting'

urlpatterns = [
    path('', views.usersetting),
    path('usersetting/', views.usersetting, name='usersetting')

]

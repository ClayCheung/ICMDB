from django.urls import path
from assets import views

app_name = 'assets'

urlpatterns = [
    path('', views.assets_view , name='assets_view'),
]

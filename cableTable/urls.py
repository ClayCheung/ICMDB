from django.urls import path,re_path
from cableTable import views

app_name = 'cableTable'

urlpatterns = [
    path('import-entrance/', views.entrance, name='entrance'),
    path('other_info/', views.other_info, name='other_info')
]

from django.urls import path
from contact import views

app_name = 'contact'

urlpatterns = [
    path('', views.linkman),
    path('linkman/', views.linkman, name='linkman'),

]

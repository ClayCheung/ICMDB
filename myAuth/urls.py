from django.urls import path
from myAuth import views

app_name = 'myAuth'

urlpatterns = [
    path('login/', views.login, name='login'),

]

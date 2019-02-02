from django.urls import path
from workOrder import views

app_name = 'workOrder'

urlpatterns = [
    path('sponsor/', views.sponsor, name='sponsor'),
    path('approver/', views.approver, name='approver'),
    path('executor/', views.executor, name='executor'),
    path('create/', views.workorderCreate, name='workorderCreate'),
    path('update/', views.workorderUpdate, name='workorderUpdate'),
    path('delete/', views.workorderDelete, name='workorderDelete'),
    path('doapprove/', views.workorderApprove, name='workorderApprove'),
    path('pass/', views.workorderPass, name='workorderPass'),
    path('detail/', views.workorderDetail, name='workorderDetail'),
    path('return/', views.workorderReturn, name='workorderReturn'),
    path('handle/', views.workorderHandle, name='workorderHandle'),
    path('executed/', views.workorderExecuted, name='workorderExecuted'),
    path('download/', views.workorderDownload, name='workorderDownload')
]

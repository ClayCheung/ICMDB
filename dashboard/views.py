from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from parentView.myView import baseView

# Create your views here.


@baseView
@login_required
def dashboard(request):

    return render(request, 'dashboard/dashboard.html', locals())

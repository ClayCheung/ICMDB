from django.shortcuts import render

# Create your views here.

def usersetting(request):
    pass
    return render(request, 'sysetting/usersetting.html', locals())
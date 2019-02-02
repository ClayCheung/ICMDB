from django.shortcuts import render, redirect
from django.contrib import auth

# Create your views here.

def login(request):
    if request.method=='POST':
        # 认证
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:# 认证成功
            # 登录
            auth.login(request, user)
            # 跳转到首页
            return redirect('/')

        else:# 认证失败
            message = "登录认证失败!"
            print('登录认证失败!')



    return render(request,'myAuth/login.html', locals())
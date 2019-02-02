from django.contrib.auth import logout
from django.shortcuts import render, redirect


def baseView(func):
    def wrapper(request, *args, **kwargs):# 带被装饰的函数的参数

        # user = request.user
        # role_list = user.role.all()
        # for role in role_list:
        #     print(role)

        if request.method == 'POST' and 'logout' in request.POST:
            logout(request)
            return redirect('/')
        else:
            return func(request, *args, **kwargs)

    return wrapper # 在被装饰的函数前 执行wrapper


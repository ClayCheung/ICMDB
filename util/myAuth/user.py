from myAuth.models import UserInfo


def getUser(user_fullName):
    """
    输入用户的全名，输出用户对象
    如果输入的名称没有定位到用户对象，返回None
    :param user_fullName:
    :return:
    """
    for user_obj in UserInfo.objects.all():
        fullName = user_obj.last_name+user_obj.first_name
        if fullName==user_fullName:
            return user_obj
    return None
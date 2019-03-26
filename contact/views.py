from django.shortcuts import render
from util.workOrder.workorder import  get_lastest_WO_set
from myAuth.models import UserInfo
from ICMDB.settings import MEDIA_ROOT
import os
# Create your views here.

def linkman(request):
    saved_wo_set = get_lastest_WO_set().filter(o_state=0).filter(sponsor=request.user)
    executed_confirm_set = get_lastest_WO_set().filter(o_state__in=[5, 7]).filter(sponsor=request.user)
    wait_handle_set = get_lastest_WO_set().filter(o_state=2).filter(executor=request.user)
    wait_excute_set = get_lastest_WO_set().filter(o_state=3).filter(executor=request.user)
    need_approve_set = get_lastest_WO_set().filter(o_state__in=[1, 4]).filter(approver=request.user)

    image_path = "{0}/{1}/".format(MEDIA_ROOT, 'image')
    if not os.path.exists(image_path):
        os.makedirs(image_path)



    all_members = UserInfo.objects.exclude(username='admin')
    return render(request, 'contact/linkman.html',locals())
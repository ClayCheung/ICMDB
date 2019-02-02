from django.shortcuts import render
from django.shortcuts import HttpResponse
from workOrder.models import WorkOrder, WorkOrderNum
from myAuth.models import Role, UserInfo
from django.contrib.auth.decorators import login_required
from parentView.myView import baseView
from django.db.models import Q

from util.myAuth.user import getUser
from util.workOrder.workorder import createWorkOrderNum, get_lastest_WO_set

# Create your views here.

@baseView
@login_required
def sponsor(request):
    # print('所有最新的工单列表', get_lastest_WO_set())
    # 状态是已保存的、发起人是自己的工单的列表
    saved_wo_set = get_lastest_WO_set().filter(o_state=0).filter(sponsor=request.user)
    # print('状态是已保存的、发起人是自己的工单的列表', saved_wo_set)

    # 待我确认已经完成的工单
    executed_confirm_set = get_lastest_WO_set().filter(o_state=5).filter(sponsor=request.user)

    # 我发送的工单
    iSend_wo_set = get_lastest_WO_set().exclude(o_state=0).filter(sponsor=request.user)
    return render(request, 'workOrder/sponsor.html', locals())


@baseView
@login_required
def approver(request):
    # print('所有最新的工单列表', get_lastest_WO_set())
    # print('所有最新的工单列表', type(get_lastest_WO_set()))
    # 状态是待审批或者待重审、审批人是自己的工单的列表
    need_approve_set = get_lastest_WO_set().filter(Q(o_state=1) | Q(o_state=4)).filter(approver=request.user)
    # print('状态是待审批或者待重审、审批人是自己的工单的列表', need_approve_set)
    # 所有不是 待审批 待重审的 审批人是我自己的工单
    approved_set = get_lastest_WO_set().exclude(o_state__in=[1, 4]).filter(approver=request.user)
    return render(request, 'workOrder/approver.html', locals())



@baseView
@login_required
def executor(request):
    wait_handle_set = get_lastest_WO_set().filter(o_state=2).filter(executor=request.user)
    wait_excute_set = get_lastest_WO_set().filter(o_state=3).filter(executor=request.user)
    excuted_set = get_lastest_WO_set().filter(o_state__in=[4, 5, 6]).filter(executor=request.user)
    return render(request, 'workOrder/executor.html', locals())


@baseView
@login_required
def workorderCreate(request):
    # 获取工单类型列表
    workorder_type_list = []
    for i in range(0,len(WorkOrder.o_type_choice)):
        workorder_type_list.append(WorkOrder.o_type_choice[i][1])
    # 获取发起人
    sponsor = request.user
    # 获取审批者列表
    approver_list = []
    approver_set = Role.objects.filter(name="approver")[0].userinfo_set.all()
    for approver in approver_set:
        approver_list.append(approver.__str__())
    # 获取执行者列表
    executor_list = []
    for executor in UserInfo.objects.all():
        if executor.is_superuser!=True:
            executor_list.append(executor.__str__())




    if request.method == 'POST':
        if 'submit_save' in request.POST: # 保存工单
            print("保存工单")
            title = request.POST.get('title')
            workorder_type = request.POST.get('workorder_type')
            deadline = request.POST.get('deadline')
            project_name = request.POST.get('project_name')
            # sponsor = request.POST.get('sponsor')
            approver = request.POST.get('approver')
            executor = request.POST.get('executor')
            workorder_content = request.POST.get('workorder_content')

            attachment = request.FILES.get('attachment')

            print(title,workorder_type,deadline,project_name,sponsor,approver_list[int(approver)],executor_list[int(executor)],workorder_content,attachment)

            # 导入数据库 工单状态：保存
            WON = WorkOrderNum.objects.create(num='')
            WorkOrderNum.objects.filter(pk=WON.pk).update(num=createWorkOrderNum(WON.id))


            wo = WorkOrder.objects.create(title=title,
                                     o_type=workorder_type,
                                     deadLine=deadline,
                                     project=project_name,
                                     sponsor=sponsor,
                                     approver=getUser(approver_list[int(approver)]),
                                     executor=getUser(executor_list[int(executor)]),
                                     content=workorder_content,


                                     # state 为 已保存  工单号自动生成
                                     o_state = 0, # 工单状态-已保存
                                     workOrder_num = WON,
                                     # attachment=attachment
                                     )
            wo.attachment = attachment
            wo.save()
            return render(request, 'workOrder/sponsor.html', locals())




        elif 'submit_send' in request.POST: # 发送审批
            print("发送审批")
            title = request.POST.get('title')
            workorder_type = request.POST.get('workorder_type')
            deadline = request.POST.get('deadline')
            project_name = request.POST.get('project_name')
            # sponsor = request.POST.get('sponsor')
            approver = request.POST.get('approver')
            executor = request.POST.get('executor')
            workorder_content = request.POST.get('workorder_content')

            attachment = request.FILES.get('attachment')

            print(title, workorder_type, deadline, project_name, sponsor, approver_list[int(approver)],
                  executor_list[int(executor)], workorder_content, attachment)

            # 导入数据库 工单状态：保存
            WON = WorkOrderNum.objects.create(num='')
            WorkOrderNum.objects.filter(pk=WON.pk).update(num=createWorkOrderNum(WON.id))

            wo = WorkOrder.objects.create(title=title,
                                     o_type=workorder_type,
                                     deadLine=deadline,
                                     project=project_name,
                                     sponsor=sponsor,
                                     approver=getUser(approver_list[int(approver)]),
                                     executor=getUser(executor_list[int(executor)]),
                                     content=workorder_content,


                                     # state 为 发送审批
                                     o_state=1,  # 工单状态-发送审批
                                     workOrder_num=WON,
                                     # attachment=attachment
                                     )
            wo.attachment = attachment
            wo.save()
            return render(request, 'workOrder/sponsor.html', locals())
        elif 'submit_sendAndEmail' in request.POST: # 发送审批并且发送邮件
            print("发送审批并且发送邮件")



    return render(request, 'workOrder/workorder_create.html', locals())


@baseView
@login_required
def workorderUpdate(request):
    # 获取工单类型列表
    workorder_type_list = []
    for i in range(0, len(WorkOrder.o_type_choice)):
        workorder_type_list.append(WorkOrder.o_type_choice[i][1])
    # 获取审批者列表
    approver_list = []
    approver_set = Role.objects.filter(name="approver")[0].userinfo_set.all()
    for approver in approver_set:
        approver_list.append(approver.__str__())
    # 获取执行者列表
    executor_list = []
    for executor in UserInfo.objects.all():
        if executor.is_superuser != True:
            executor_list.append(executor.__str__())

    if request.method=='GET':
        id = request.GET.get('id')
        wo = WorkOrder.objects.get(id=id)
        wo_attaName = str(wo.attachment).split('/')[2]
        approver_index =  approver_list.index(wo.approver.__str__())
        executor_index = executor_list.index(wo.executor.__str__())

        return render(request, 'workOrder/workorder_update.html', locals())

    if request.method == 'POST':
        if 'submit_save' in request.POST: # 保存工单
            print("保存更新工单")
            title = request.POST.get('title')
            workorder_type = request.POST.get('workorder_type')
            deadline = request.POST.get('deadline')
            project_name = request.POST.get('project_name')
            # sponsor = request.POST.get('sponsor')
            approver = request.POST.get('approver')
            executor = request.POST.get('executor')
            workorder_content = request.POST.get('workorder_content')

            attachment = request.FILES.get('attachment')

            id = request.POST.get('wo_id')

            # 更新数据库 工单状态：保存

            wo = WorkOrder.objects.filter(id=id)
            wo.update(title=title,
                      o_type=workorder_type,
                      deadLine=deadline,
                      project=project_name,
                      approver=getUser(approver_list[int(approver)]),
                      executor=getUser(executor_list[int(executor)]),
                      content=workorder_content,
                      attachment=attachment,
                      )


            return render(request, 'workOrder/sponsor.html', locals())




        elif 'submit_send' in request.POST:  # 发送审批
            print("发送审批")
            title = request.POST.get('title')
            workorder_type = request.POST.get('workorder_type')
            deadline = request.POST.get('deadline')
            project_name = request.POST.get('project_name')
            approver = request.POST.get('approver')
            executor = request.POST.get('executor')
            workorder_content = request.POST.get('workorder_content')
            attachment = request.FILES.get('attachment')
            id = request.POST.get('wo_id')

            # 更新工单并发送至审批人审批 工单状态：待审批

            wo = WorkOrder.objects.filter(id=id)
            wo.update(title=title,
                      o_type=workorder_type,
                      deadLine=deadline,
                      project=project_name,
                      approver=getUser(approver_list[int(approver)]),
                      executor=getUser(executor_list[int(executor)]),
                      content=workorder_content,
                      attachment=attachment,

                      o_state=1,  #工单状态：待审批
                      )
            return render(request, 'workOrder/sponsor.html', locals())


        elif 'submit_sendAndEmail' in request.POST:  # 发送审批并且发送邮件
            print("发送审批并且发送邮件")





@baseView
@login_required
def workorderDelete(request):
    if request.method=='POST':
        id = request.POST.get('id')
        print('删除id', id)
        wo = WorkOrderNum.objects.get(id=id)
        wo.delete()
        return id
    return False

@baseView
@login_required
def workorderApprove(request):
    # 获取工单类型列表
    workorder_type_list = []
    for i in range(0, len(WorkOrder.o_type_choice)):
        workorder_type_list.append(WorkOrder.o_type_choice[i][1])
    # 获取审批者列表
    approver_list = []
    approver_set = Role.objects.filter(name="approver")[0].userinfo_set.all()
    for approver in approver_set:
        approver_list.append(approver.__str__())
    # 获取执行者列表
    executor_list = []
    for executor in UserInfo.objects.all():
        if executor.is_superuser != True:
            executor_list.append(executor.__str__())

    if request.method=='GET':
        id = request.GET.get('id')
        wo = WorkOrder.objects.get(id=id)
        wo_attaName = str(wo.attachment).split('/')[2]
        approver_index =  approver_list.index(wo.approver.__str__())
        executor_index = executor_list.index(wo.executor.__str__())

        return render(request, 'workOrder/workorder_approve.html', locals())


    if request.method == 'POST':
        if 'submit_pass' in request.POST:  # 工单 审批通过
            print("审批通过")
            title = request.POST.get('title')
            workorder_type = request.POST.get('workorder_type')
            deadline = request.POST.get('deadline')
            project_name = request.POST.get('project_name')
            sponsor = request.POST.get('sponsor')
            approver = request.POST.get('approver')
            executor = request.POST.get('executor')
            workorder_content = request.POST.get('workorder_content')

            attachment = request.FILES.get('attachment')

            id = request.POST.get('wo_id')
            pre_wo = WorkOrder.objects.get(id=id)

            # 更新数据库 工单状态：审批通过 ，创建一个新的工单状态为审批通过

            WorkOrder.objects.create(title=title,
                                     o_type=workorder_type,
                                     deadLine=deadline,
                                     project=project_name,
                                     sponsor=pre_wo.sponsor,
                                     approver=pre_wo.approver,
                                     executor=getUser(executor_list[int(executor)]),
                                     content=workorder_content,
                                     attachment=pre_wo.attachment,

                                     # state 为 审批通过-待接单
                                     o_state=2,  # 工单状态-审批通过-待接单
                                     # 同一个任务流 工单号不变
                                     workOrder_num=pre_wo.workOrder_num,
                                     )


            return render(request, 'workOrder/sponsor.html', locals())


        if 'submit_reject' in request.POST:  # 工单 审批通过
            print("驳回申请")

            id = request.POST.get('wo_id')
            pre_wo = WorkOrder.objects.get(id=id)
            # 更新数据库 工单状态：驳回申请 ，创建一个新的工单状态为驳回申请

            WorkOrder.objects.create(title=pre_wo.title,
                                     o_type=pre_wo.o_type,
                                     deadLine=pre_wo.deadLine,
                                     project=pre_wo.project,
                                     sponsor=pre_wo.sponsor,
                                     approver=pre_wo.approver,
                                     executor=pre_wo.executor,
                                     content=pre_wo.content,
                                     attachment=pre_wo.attachment,

                                     # state 为 驳回申请
                                     o_state=7,  # 工单状态-驳回申请
                                     # 同一个任务流 工单号不变
                                     workOrder_num=pre_wo.workOrder_num,
                                     )

            return render(request, 'workOrder/sponsor.html', locals())


@baseView
@login_required
def workorderPass(request):
    if request.method=='POST':
        id = request.POST.get('id')
        print('直接审批通过id：', id)
        pre_wo = WorkOrder.objects.get(id=id)
        # 更新数据库 工单状态：驳回申请 ，创建一个新的工单状态为驳回申请

        WorkOrder.objects.create(title=pre_wo.title,
                                 o_type=pre_wo.o_type,
                                 deadLine=pre_wo.deadLine,
                                 project=pre_wo.project,
                                 sponsor=pre_wo.sponsor,
                                 approver=pre_wo.approver,
                                 executor=pre_wo.executor,
                                 content=pre_wo.content,
                                 attachment=pre_wo.attachment,

                                 # state 为 审批通过-待接单
                                 o_state=2,  # 工单状态-审批通过-待接单
                                 # 同一个任务流 工单号不变
                                 workOrder_num=pre_wo.workOrder_num,
                                 )
        return id
    return False


@baseView
@login_required
def workorderDetail(request):
    if request.method=='GET':
        id = request.GET.get('id')

        wo = WorkOrder.objects.get(id=id)
        # wo_attaName = str(wo.attachment).split('/')[2]
        wo_attaName =  '' if str(wo.attachment)=='' else str(wo.attachment).split('/')[2]
        return render(request, 'workOrder/workorder_detail.html', locals())

    return render(request, 'workOrder/workorder_detail.html', locals())

@baseView
@login_required
def workorderReturn(request):
    if request.method=='POST':
        id = request.POST.get('id')
        print('回退工单id :', id)
        pre_wo = WorkOrder.objects.get(id=id)
        # 更新数据库 工单状态：待重审，创建一个新的工单状态为待重审
        WorkOrder.objects.create(title=pre_wo.title,
                                 o_type=pre_wo.o_type,
                                 deadLine=pre_wo.deadLine,
                                 project=pre_wo.project,
                                 sponsor=pre_wo.sponsor,
                                 approver=pre_wo.approver,
                                 executor=pre_wo.executor,
                                 content=pre_wo.content,
                                 attachment=pre_wo.attachment,
                                 # 同一个任务流 工单号不变
                                 workOrder_num=pre_wo.workOrder_num,

                                 # state 为 审批通过-待重审
                                 o_state=4,  # 工单状态-审批通过-待重审

                                 )
        return id
    return False




@baseView
@login_required
def workorderHandle(request):
    if request.method=='POST':
        id = request.POST.get('id')
        print('接单-工单id :', id)
        pre_wo = WorkOrder.objects.get(id=id)
        # 更新数据库 工单状态：待执行，创建一个新的工单状态为待执行
        WorkOrder.objects.create(title=pre_wo.title,
                                 o_type=pre_wo.o_type,
                                 deadLine=pre_wo.deadLine,
                                 project=pre_wo.project,
                                 sponsor=pre_wo.sponsor,
                                 approver=pre_wo.approver,
                                 executor=pre_wo.executor,
                                 content=pre_wo.content,
                                 attachment=pre_wo.attachment,
                                 # 同一个任务流 工单号不变
                                 workOrder_num=pre_wo.workOrder_num,

                                 # state 为 待执行
                                 o_state=3,  # 状态改为 待执行 确认接单

                                 )
        return id
    return False


@baseView
@login_required
def workorderExecuted(request):
    if request.method=='POST':
        id = request.POST.get('id')
        print('已执行id :', id)
        pre_wo = WorkOrder.objects.get(id=id)
        # 更新数据库 工单状态：待确认完成，创建一个新的工单状态为待确认完成
        WorkOrder.objects.create(title=pre_wo.title,
                                 o_type=pre_wo.o_type,
                                 deadLine=pre_wo.deadLine,
                                 project=pre_wo.project,
                                 sponsor=pre_wo.sponsor,
                                 approver=pre_wo.approver,
                                 executor=pre_wo.executor,
                                 content=pre_wo.content,
                                 attachment=pre_wo.attachment,
                                 # 同一个任务流 工单号不变
                                 workOrder_num=pre_wo.workOrder_num,

                                 # state 为 待确认完成
                                 o_state=5,  # 状态改为 待确认完成

                                 )
        return id
    return False



@baseView
@login_required
def workorderDownload(request):
    if request.method=='POST':
        id = request.POST.get('id')
        print('下载工单附件 id :', id)
        attachFile = WorkOrder.objects.get(id=id).attachment

        response = HttpResponse(attachFile)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="netDev_info.csv"'
        return response
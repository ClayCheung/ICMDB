from django.shortcuts import render
from .models import *
from util.cableTable import tools
from util.assets import orm
from util.network import description
from django.contrib.auth.decorators import login_required
from parentView.myView import baseView

# Create your views here.

@baseView
@login_required
def assets_view(request):

    project_name_list = []
    for p in Project.objects.all():
        project_name_list.append(p.name)




    if request.method == 'POST' and 'submit_viewProject' in request.POST:
        """
        查看已有项目信息
        """

        p_name_id = request.POST.get('exist_project')
        p_name = project_name_list[int(p_name_id)]
        this_project = Project.objects.filter(name=p_name)[0]

        netDevObjList = NetworkDevice.objects.filter(asset__project=this_project)
        serverDevObjList = Server.objects.filter(asset__project=this_project)
        storDevObjList = StorDevice.objects.filter(asset__project=this_project)

    if request.method == 'POST' and 'submit_projectInfo' in request.POST:
        """
        创建新项目，导入项目信息
        """
        project_name = request.POST.get('project_name')

        p_administrator = request.POST.get('project_administrator')
        p_system = request.POST.get('project_system')
        p_platform = request.POST.get('project_platform')
        p_module = request.POST.get('project_module')
        p_department = request.POST.get('project_department')

        cabletable = request.FILES.get("cabletable")

        # 把信息导入数据库
        ## 项目信息 导入
        defaults = {
            'department': p_department,
            'system': p_system,
            'module': p_module,
            'platform': p_platform,
            'company': "浙江移动",
            'administrator': p_administrator,

        }
        if project_name != '':
            this_project = Project.objects.update_or_create(name=project_name,
                                             defaults=defaults)[0]

        ## 布线表中的所有信息 导入
        cabletableFile = CableTableFille(file=cabletable, name=cabletable.name,
                                         project=Project.objects.filter(name=project_name)[0])
        cabletableFile.save()

        ####

        csv_info = request.FILES.get("netinfo_plus")

        csv_data = csv_info.read().decode('gbk')
        lines = csv_data.split(',,,,\r\n')[1:]
        # print(len(lines))

        serverDevList = tools.getServerDeviceList(cabletableFile.file.path)
        storDevList = tools.getStorDeviceList(cabletableFile.file.path)

        for row in lines:
            fields = row.strip('\r\n').split(',')
            if fields[1] != '':
                Asset.objects.update_or_create(name=fields[0].strip(),
                                               defaults={
                                                   'asset_type': 'networkdevice',
                                                   'sysname': fields[1].strip(),
                                                   'project': this_project,
                                                   'vender': fields[3].strip(),
                                                   'model': fields[4].strip(),
                                               })

                NetworkDevice.objects.update_or_create(asset=Asset.objects.filter(name=fields[0].strip())[0],
                                                       defaults={
                                                           'sub_asset_type': tools.mapSubTypeId(fields[2].strip()),
                                                       })

                orm.update_or_create_cabinetNum(fields[0].strip(),
                                                tools.get_cabinetNum(fields[0].strip(), cabletableFile.file.path))
            else:# 如果sysname不填，视为server来入资产
                    serverDevList.append(fields[0].strip())


        for devName in serverDevList:
            orm.update_or_create_assetType(devName, 'server')
            orm.update_or_create_cabinetNum(devName, tools.get_cabinetNum(devName, cabletableFile.file.path))
            orm.update_or_create_vender(devName, tools.parse_serverVender(devName))
            orm.update_or_create_model(devName, tools.parse_serverModel(devName))
            Asset.objects.update_or_create(name=devName, defaults={
                'project': this_project,
            })
            orm.map_ServerToAsset(devName)

        for devName in storDevList:
            orm.update_or_create_assetType(devName, 'storagedevice')
            orm.update_or_create_cabinetNum(devName, tools.get_cabinetNum(devName, cabletableFile.file.path))
            orm.update_or_create_vender(devName, tools.parse_storVender(devName))
            orm.update_or_create_model(devName, tools.parse_storModel(devName))
            Asset.objects.update_or_create(name=devName, defaults={
                'project': this_project,
            })
            orm.map_StorDeviceToAsset(devName)





        netDevObjList = NetworkDevice.objects.filter(asset__project=this_project)
        serverDevObjList = Server.objects.filter(asset__project=this_project)
        storDevObjList = StorDevice.objects.filter(asset__project=this_project)


        # 跟新或保存 所有非网络设备的sysname

        for dev in serverDevObjList:
            dev.asset.sysname = dev.asset.name
            dev.asset.save()
        for dev in storDevObjList:
            dev.asset.sysname = dev.asset.name
            dev.asset.save()



        # 检测布线表的每一行：port命名是否合规，如果不合规则输出错误日志，
        # 如果合规，则添加port对象并映射到asset
        err_portFormat_log = orm.checkPort_and_mapToAsset(cabletableFile.file.path)

        # 检测布线表的每一行：每一行 定位到数据库的2个port，OneToOne关联之
        # 如果1个port关联至多个port， 输出错误日志
        err_portMutiAssign_log = orm.assignPortToPort(cabletableFile.file.path)

        # 检测相同sysname的资产下是否有重复的端口，通常堆叠的设备chassis号都写1就会引起这个问题

        warn_samePort_log = orm.check_samePort_on_stackDev(this_project)

        ###
        ###
        ###
        # 生成描述配置信息


        stackDev_Set = []


        for asset_Obj in netDevObjList.filter(sub_asset_type__in=[0, 1, 4]):# 属于交换机 路由器 防火墙的网络设备
            if len(netDevObjList.filter(asset__sysname=asset_Obj.asset.sysname)) == 2:  # 如果是堆叠设备
                stackDev_Set.append(asset_Obj)

        print(stackDev_Set)

        description.create_descriptions(stackDev_Set)



    return render(request, 'assets/assets_view.html', locals())

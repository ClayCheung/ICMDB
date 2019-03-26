from django.shortcuts import render
from django.shortcuts import HttpResponse, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import CableTableFille, Project, NetworkDevice, Server, StorDevice, Asset , Locate
from util.cableTable import tools, orm
import csv, os
from ICMDB.settings import CSV_ROOT
from parentView.myView import baseView
from django.contrib.auth.decorators import login_required


# Create your views here.

@baseView
@login_required
def entrance(request):
    """
    导入布线表的入口，从布线表中提取数据，检查后，导入数据库
    :param request:
    :return:
    """

    # if request.method == 'POST':
    if request.method == 'POST' and 'submit_cableTable' in request.POST:
        cabletable = request.FILES.get("cabletable")
        project_name = request.POST.get('project_name')

        # print(type(cabletable))
        # print(project_name)
        Project.objects.update_or_create(name=project_name)
        # print( Project.objects.filter(name=project_name))
        # print(cabletable,type(cabletable))
        cabletableFile = CableTableFille(file=cabletable, name=cabletable.name, project=Project.objects.filter(name=project_name)[0])
        cabletableFile.save()

        # 解析布线表-导出网络设备资产名list函数
        # print(cabletableFile.file.path)
        netDeviceList = tools.getNetDeviceList(cabletableFile.file.path)




    return render(request, 'cableTable/importTable.html', locals())


@csrf_exempt
@baseView
@login_required
def other_info(request):
    """
    填入《附件信息表》,传入数据库
    :param request:
    :return:
    """


    if request.method == 'POST' and 'submit_export' in request.POST:
        """
        导出 csv格式的 附加信息表
        """
        sysname_l = request.POST.getlist('sysname')
        e_type_l = request.POST.getlist('e_type')
        e_vender_l = request.POST.getlist('e_vender')
        e_model_l = request.POST.getlist('e_model')

        # 选择最新保存的布线表
        cabletableFile = CableTableFille.objects.order_by('-c_time')[0]
        # 导出 网络设备资产名列表
        netDeviceList = tools.getNetDeviceList(cabletableFile.file.path)

        # 生成 CSV

        p_path = "{0}/{1}/".format(CSV_ROOT, cabletableFile.project.name)
        if not os.path.exists(p_path):
            os.makedirs(p_path)

        csv_fpath = CSV_ROOT+'\\'+cabletableFile.project.name+'_附加信息.csv'

        with open(csv_fpath, 'w+', encoding='GBK') as csvfile:
            fieldnames = ['资产名', 'sysname', '类型', '厂商', '型号']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)



            writer.writeheader()
            for id, netDevName in enumerate(netDeviceList):
                writer.writerow({'资产名': netDevName,
                                 'sysname': sysname_l[id],
                                 '类型': tools.mapSubType(e_type_l[id]),
                                 '厂商': tools.mapVender(e_type_l[id], e_vender_l[id]),
                                 '型号': tools.mapModel(e_type_l[id], e_vender_l[id], e_model_l[id])})


        file = open(csv_fpath, 'r+', encoding='GBK')
        response = HttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="netDev_info.csv"'
        return response





    if request.method == 'POST' and 'submit_plus' in request.POST:
        """
        导入附加信息
        """
        # 获取html中提交的form表单，表单中的多个input的name相同，
        if request.FILES.get('submit_import')!=None:
            """
            通过 导入 csv格式的附加信息表 来导入附加信息
            """
            print('looooooooooooook!-1')

            # 选择最新保存的布线表
            cabletableFile = CableTableFille.objects.order_by('-c_time')[0]
            this_project = cabletableFile.project


            csv_info = request.FILES.get("submit_import")


            csv_data = csv_info.read().decode('gbk')
            lines = csv_data.split(',,,,\r\n')[1:]
            # print(len(lines))

            serverDevList = tools.getServerDeviceList(cabletableFile.file.path)
            storDevList = tools.getStorDeviceList(cabletableFile.file.path)

            for row in lines:
                fields = row.strip('\r\n').split(',')
                if fields[1]!='':
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

                    orm.update_or_create_cabinetNum(fields[0].strip(), tools.get_cabinetNum(fields[0].strip(), cabletableFile.file.path))
                else:# 如果sysname不填，视为server来入资产
                    serverDevList.append(fields[0].strip())
            for devName in serverDevList:
                orm.update_or_create_assetType(devName, 'server')
                orm.update_or_create_cabinetNum(devName, tools.get_cabinetNum(devName, cabletableFile.file.path))
                orm.update_or_create_vender(devName, tools.parse_serverVender(devName))
                orm.update_or_create_model(devName, tools.parse_serverModel(devName))
                Asset.objects.update_or_create(name=devName, defaults={
                    'project': cabletableFile.project,
                })
                orm.map_ServerToAsset(devName)

            for devName in storDevList:
                orm.update_or_create_assetType(devName, 'storagedevice')
                orm.update_or_create_cabinetNum(devName, tools.get_cabinetNum(devName, cabletableFile.file.path))
                orm.update_or_create_vender(devName, tools.parse_storVender(devName))
                orm.update_or_create_model(devName, tools.parse_storModel(devName))
                Asset.objects.update_or_create(name=devName, defaults={
                    'project': cabletableFile.project,
                })
                orm.map_StorDeviceToAsset(devName)

            netDevObjList = NetworkDevice.objects.filter(asset__project=cabletableFile.project)
            serverDevObjList = Server.objects.filter(asset__project=cabletableFile.project)
            storDevObjList = StorDevice.objects.filter(asset__project=cabletableFile.project)

            return render(request, 'cableTable/startCheckUp.html', locals())


        else:
            """
            通过手工填入，来导入附加信息
            """
            print('looooooooooooook!-2')
            sysname_l = request.POST.getlist('sysname')
            e_type_l = request.POST.getlist('e_type')
            e_vender_l = request.POST.getlist('e_vender')
            e_model_l = request.POST.getlist('e_model')

            # 选择最新保存的布线表
            cabletableFile = CableTableFille.objects.order_by('-c_time')[0]
            this_project = cabletableFile.project
            # print(cableTableFile.c_time)

            netDeviceList = tools.getNetDeviceList(cabletableFile.file.path)



            # print(netDeviceList)

            for id,netDevName in enumerate(netDeviceList):
                # print(id)
                # print(netDevName)
                # print(sysname_l[id])
                # print(e_type_l[id])
                # print(e_vender_l[id])
                # print(e_model_l[id])
                # print('---------------------')

                # 如果填入的sysname不是空的，则导入网络设备资产信息至数据库
                if sysname_l[id]!='':
                    Asset.objects.update_or_create(name=netDevName,
                                                   defaults={
                                                       'asset_type': 'networkdevice',
                                                       'sysname': sysname_l[id],
                                                       'project': this_project,
                                                       'vender': tools.mapVender(e_type_l[id], e_vender_l[id]),
                                                       'model': tools.mapModel(e_type_l[id], e_vender_l[id], e_model_l[id]),
                                                   })

                    NetworkDevice.objects.update_or_create(asset=Asset.objects.filter(name=netDevName)[0],
                                                           defaults={
                                                               'sub_asset_type': int(e_type_l[id]),
                                                           })


            # 把布线表中部分信息(网络设备的机柜号、服务器和存储设备的 名称 机柜 厂商 型号) 存入数据库

            for devName in netDeviceList:
                orm.update_or_create_cabinetNum(devName, tools.get_cabinetNum(devName, cabletableFile.file.path))

            serverDevList =  tools.getServerDeviceList(cabletableFile.file.path)
            storDevList = tools.getStorDeviceList(cabletableFile.file.path)

            for devName in serverDevList:
                orm.update_or_create_assetType(devName, 'server')
                orm.update_or_create_cabinetNum(devName, tools.get_cabinetNum(devName, cabletableFile.file.path))
                orm.update_or_create_vender(devName, tools.parse_serverVender(devName))
                orm.update_or_create_model(devName, tools.parse_serverModel(devName))
                Asset.objects.update_or_create(name=devName, defaults={
                                           'project': cabletableFile.project,
                                       })
                orm.map_ServerToAsset(devName)

            for devName in storDevList:
                orm.update_or_create_assetType(devName, 'storagedevice')
                orm.update_or_create_cabinetNum(devName, tools.get_cabinetNum(devName, cabletableFile.file.path))
                orm.update_or_create_vender(devName, tools.parse_storVender(devName))
                orm.update_or_create_model(devName, tools.parse_storModel(devName))
                Asset.objects.update_or_create(name=devName, defaults={
                                            'project': cabletableFile.project,
                                        })
                orm.map_StorDeviceToAsset(devName)

            # 定义一个list list的值为本项目内的所有网络设备资产
            # 定义一个list list的值为本项目内的所有服务器资产
            # 定义一个list list的值为本项目内的所有存储设备资产

            netDevObjList = NetworkDevice.objects.filter(asset__project=cabletableFile.project)
            # print(netDevObjList[0].asset.name)
            serverDevObjList = Server.objects.filter(asset__project=cabletableFile.project)
            print(serverDevObjList[0].asset.name)
            storDevObjList = StorDevice.objects.filter(asset__project=cabletableFile.project)

            return render(request, 'cableTable/startCheckUp.html', locals())



    # if request.method == "POST" and request.POST.getlist('sysname') == []:# 如果传入的POST值是空的，说明点了“开始检查”
    if request.method == 'POST' and 'start_check' in request.POST:# 如果传入的request中包含‘start_check’，说明点了“开始检查”
        print('到这里了，提交了！！！！！！！！')


        # 选择最新保存的布线表
        cabletableFile = CableTableFille.objects.order_by('-c_time')[0]

        # 定义一个list list的值为本项目内的所有网络设备资产
        # 定义一个list list的值为本项目内的所有服务器资产
        # 定义一个list list的值为本项目内的所有存储设备资产
        netDevObjList = NetworkDevice.objects.filter(asset__project=cabletableFile.project)
        serverDevObjList = Server.objects.filter(asset__project=cabletableFile.project)
        storDevObjList = StorDevice.objects.filter(asset__project=cabletableFile.project)
        # 跟新或保存 所有非网络设备的sysname

        for dev in serverDevObjList:
            print(dev)
            print(dev.asset.project)
            print(cabletableFile.project)
            print(dev.asset.name)
            dev.asset.sysname = dev.asset.name
            dev.asset.save()
        for dev in storDevObjList:
            dev.asset.sysname = dev.asset.name
            dev.asset.save()

        # 检测机柜号是否和资产名匹配
        err_cabinetNum_log = tools.check_cabinetNum(cabletableFile.file.path)

        # 检测布线表的每一行：port命名是否合规，如果不合规则输出错误日志，
        # 如果合规，则添加port对象并映射到asset
        err_portFormat_log = orm.checkPort_and_mapToAsset(cabletableFile.file.path)

        # 检测布线表的每一行：每一行 定位到数据库的2个port，OneToOne关联之
        # 如果1个port关联至多个port， 输出错误日志
        err_portMutiAssign_log = orm.assignPortToPort(cabletableFile.file.path)

        # 检测相同sysname的资产下是否有重复的端口，通常堆叠的设备chassis号都写1就会引起这个问题

        warn_samePort_log = orm.check_samePort_on_stackDev(cabletableFile.project)

    if request.method == 'POST' and 'reset_data' in request.POST:
        Project.objects.all().delete()
        Locate.objects.all().delete()

        return render(request, 'dashboard/dashboard.html', locals())


    return render(request, 'cableTable/startCheckUp.html', locals())



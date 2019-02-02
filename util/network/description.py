import os
from util.tools import networkTools
from assets.models import DescFile


def create_descriptions(stackDev_ObjSet):
    """
    :param stackDev_ObjSet: 这是一个networkDev_Obj的子集合
    :return:
    """
    this_project = stackDev_ObjSet[0].asset.project
    p_path = "media/downloads/project_【{0}】/网络集成/02-描述配置/".format(this_project.name)
    if not os.path.exists(p_path):
        os.makedirs(p_path)


    for dev in stackDev_ObjSet:
        # print(os.getcwd())


        filename = dev.asset.sysname+'.txt'

        cfg_lines = []

        for p in dev.asset.port_set.all():




            cfg_0 = networkTools.getPortName(networkTools.mapPortType(p.asset.vender, p.speed)+' ',
                                             p.chassisNum,p.slotNum, p.subSlotNum, p.portNum)


            cfg_0 = 'interface '+ cfg_0

            if p.remotePort!=None:
                cfg_descr = "description TO_[{0}]_{1}".format(p.remotePort.asset.name, networkTools.getPortName(p.remotePort.get_speed_display(),
                                                 p.remotePort.chassisNum,p.remotePort.slotNum, p.remotePort.subSlotNum, p.remotePort.portNum))
            else:
                cfg_descr = "description TO_[{0}]_{1}".format(p.port.asset.name, networkTools.getPortName(p.port.get_speed_display(),
                                                 p.port.chassisNum, p.port.slotNum, p.port.subSlotNum, p.port.portNum))
            cfg = cfg_0+'\n'+cfg_descr+'\n'
            cfg_lines.append(cfg)

        with open(p_path+filename, 'a+', encoding='UTF-8') as f:
            f.writelines(cfg_lines)




    return 0

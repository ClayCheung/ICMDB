from workOrder.models import WorkOrderNum, WorkOrder


def createWorkOrderNum(id):
    """
    输入id，生成工单号
    :param id:
    :return:
    """
    num = "%06d" % id
    logo = "HS"
    return logo+num

def get_lastest_WO_set():
    """
    返回所有工单（最新状态的实例）
    :return:
    """
    won_set = WorkOrder.objects.filter(id=-1)
    # print('应该是个空集', won_set)
    # print('类型应该qset', type(won_set))
    for WON in WorkOrderNum.objects.all():
        # print('在循环：', WON)
        # print('应该是某个最新状态的工单',WON.workorder_set.order_by('-c_time')[:1])
        # print('类型应该qset',type(WON.workorder_set.order_by('-c_time')[:1]))
        # print('应该是个空集-2', won_set)
        lastest_wo = WON.workorder_set.order_by('-c_time')[0]
        won_set = won_set | (WON.workorder_set.filter(id=lastest_wo.id))

        # print('应该是很多最新的工单', won_set)
        # print('类型应该qset',type(won_set))
    return won_set
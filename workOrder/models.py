from django.db import models
from myAuth.models import UserInfo

# Create your models here.

class WorkOrderNum(models.Model):
    """工单号"""
    num = models.CharField(max_length=64, verbose_name="工单号")
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='工单发起日期')

    def __str__(self):
        return self.num

    class Meta:
        verbose_name = '工单号'
        verbose_name_plural = '工单号'
        ordering = ['-c_time']


def attachment_directory_path(instance, filename):
    # 文件上传到MEDIA_ROOT/workOrder/工单号/工单标题-id 目录中
    return 'workOrder/【{0}】/{1}'.format(instance.project, instance.attachment)


class WorkOrder(models.Model):
    """工单"""

    o_type_choice = (
        (0, '规划设计'),
        (1, '集成实施-硬件'),
        (2, '集成实施-网络'),
        (3, '集成实施-服务器'),
        (4, '集成实施-软件'),
        (5, '入网交维-安全加固'),
        (6, '入网交维-入网提交'),
    )

    o_state_choice = (
        (0, '已保存'),
        (1, '待审批'),
        (2, '审批通过-待接单'),
        (3, '待执行'),
        (4, '待重审'),
        (5, '待确认完成'),
        (6, '已完成'),
        (7, '驳回申请'),
    )

    workOrder_num = models.ForeignKey(WorkOrderNum, on_delete=models.CASCADE, verbose_name="工单号")
    title = models.CharField(max_length=64, verbose_name="工单标题")
    o_type = models.SmallIntegerField(choices=o_type_choice, default=0, verbose_name="工单类型")
    o_state = models.SmallIntegerField(choices=o_state_choice, verbose_name="工单状态")
    deadLine = models.DateTimeField(verbose_name="截止日期")
    project = models.CharField(max_length=64, verbose_name="所属项目")
    content = models.TextField(verbose_name="工单内容")
    attachment = models.FileField(upload_to=attachment_directory_path, null=True, blank=True, verbose_name="附件" )

    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')

    sponsor = models.ForeignKey(UserInfo, related_name='sponsor', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="发起人")
    approver = models.ForeignKey(UserInfo, related_name='approver', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="审批人")
    executor = models.ForeignKey(UserInfo, related_name='executor', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="执行人")


    def __str__(self):
        # 内置get_FOO_display()方法返回choice字段：asset_type 的第二元素的值
        return '<%s>  %s' % (self.get_o_type_display(), self.title)

    class Meta:
        verbose_name = '工单'
        verbose_name_plural = '工单'
        ordering = ['-c_time']

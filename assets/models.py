from django.db import models
from util.tools.networkTools import getPortName

# Create your models here.


class Locate(models.Model):
    def __str__(self):
        return '%s-%s-%s%s' % (self.region, self.machine_room, self.cabinet, self.cabinet_num)

    region = models.CharField(max_length=10, verbose_name="数据中心")
    machine_room = models.CharField(max_length=10,  verbose_name="机房")
    cabinet = models.CharField(max_length=2, verbose_name="机柜")
    cabinet_num = models.CharField(max_length=2, verbose_name="机柜号")

    class Meta:
        verbose_name = '设备位置'
        verbose_name_plural = "设备位置"


class Project(models.Model):
    def __str__(self):
        return  self.name

    name = models.CharField(max_length=20, verbose_name="项目名")
    department = models.CharField(max_length=20, null=True, blank=True,verbose_name="业务归属科室")
    system = models.CharField(max_length=20, null=True, blank=True,verbose_name="所属业务系统")
    module = models.CharField(max_length=20, null=True, blank=True,verbose_name="所属业务模块")
    platform = models.CharField(max_length=20, null=True, blank=True,verbose_name="所属业务平台")
    company = models.CharField(max_length=20, null=True, blank=True,verbose_name="所属业务公司")
    administrator = models.CharField(max_length=32, null=True, blank=True,verbose_name="项目管理员")

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = "项目"


class Asset(models.Model):
    """所有资产的共有数据表"""
    asset_type_choice = (
        ('server', '服务器'),
        ('networkdevice', '网络设备'),
        ('storagedevice', '存储设备'),
    )

    asset_type = models.CharField(choices=asset_type_choice, max_length=64, default='server', verbose_name="资产类型")
    name = models.CharField(max_length=64, unique=True, verbose_name="资产名称")    # 不可重复
    sysname = models.CharField(max_length=64, verbose_name="sysname")    # 不可重复
    project = models.ForeignKey('Project', null=True, blank=True, verbose_name='所属项目', on_delete=models.CASCADE)  # 该字段可以为空null
    locate = models.ForeignKey('Locate', null=True, blank=True, verbose_name='所在位置', on_delete=models.CASCADE)
    vender = models.CharField(max_length=32, null=True, blank=True, verbose_name="设备厂商")
    model = models.CharField(max_length=128, null=True, blank=True, verbose_name="设备型号")
    memo = models.TextField(null=True, blank=True, verbose_name='备注')
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')

    def __str__(self):
        # 内置get_FOO_display()方法返回choice字段：asset_type 的第二元素的值
        return '<%s>  %s' % (self.get_asset_type_display(), self.name)

    class Meta:
        verbose_name = '资产总表'
        verbose_name_plural = '资产总表'
        ordering = ['-c_time']


class Server(models.Model):
    """服务器设备"""
    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)  # 关键的一对一关联，继承Asset中所有字段


    def __str__(self):
        return '<%s> ： %s' % (self.asset.model, self.asset.name)

    class Meta:
        verbose_name = '服务器'
        verbose_name_plural = "服务器"


class StorDevice(models.Model):
    """存储设备"""
    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)  # 关键的一对一关联，继承Asset中所有字段


    def __str__(self):
        return '<%s> ： %s' % (self.asset.model, self.asset.name)

    class Meta:
        verbose_name = '存储设备'
        verbose_name_plural = '存储设备'


class NetworkDevice(models.Model):
    """网络设备"""
    sub_asset_type_choice = (
        (0, '交换机'),
        (1, '防火墙'),
        (2, '负载均衡器'),
        (3, 'SAN交换机'),
        (4, '路由器')
    )

    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, default=0, verbose_name="网络设备类型")

    def __str__(self):
        return '%s : %s--<%s>--%s' % (self.get_sub_asset_type_display(), self.asset.name, self.asset.sysname, self.asset.model)

    class Meta:
        verbose_name = '网络设备'
        verbose_name_plural = "网络设备"


class Port(models.Model):
    speed_choice = (
        (1, 'G'),
        (10, 'XG'),
        (40, '40G'),
        (100, '100G'),
        (None,None)
    )

    asset = models.ForeignKey('Asset', on_delete=models.CASCADE)  # 通过外键关联Asset。一台资产设备有多个端口。
    speed = models.SmallIntegerField(choices=speed_choice, null=True, blank=True, default=None,verbose_name="端口速率")
    chassisNum = models.SmallIntegerField(null=True, blank=True, default=None, verbose_name="机框号")
    slotNum = models.SmallIntegerField(null=True, blank=True, default=None, verbose_name="板卡槽位号")
    subSlotNum = models.SmallIntegerField(null=True, blank=True, default=None, verbose_name="子板卡槽位号")
    portNum = models.CharField(max_length=16, verbose_name="端口号")
    remotePort = models.OneToOneField('self', null=True, blank=True, on_delete=models.SET_NULL)   # 一对一映射对端端口



    def __str__(self):
        return '%s : %s' % (self.asset.sysname, getPortName(self.get_speed_display(), self.chassisNum, self.slotNum, self.subSlotNum, self.portNum))  # 用于生产description的时候调用

    class Meta:
        verbose_name = '端口名'
        verbose_name_plural = '端口名'
        # (unique_together联合约束)同一资产下的端口，必须唯一
        unique_together = ('asset', 'speed', 'chassisNum', 'slotNum', 'subSlotNum', 'portNum')


#######################  布线表文件导入数据库  ########################

def basefile_directory_path(instance, filename):
    # 文件上传到MEDIA_ROOT/uploads/project_<name>/<filename>目录中
    return 'downloads/project_【{0}】/布线表/{1}'.format(instance.project.name, instance.name)

class CableTableFille(models.Model):
    def __str__(self):
        return '%s <布线表>: %s' % (self.project.name, self.name)

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file = models.FileField(upload_to=basefile_directory_path)

    name = models.CharField(max_length=64)
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')

    class Meta:
        verbose_name = '布线表'
        verbose_name_plural = '布线表'
        ordering = ['-c_time']





#######################  网络设备描述配置文件导入数据库  ########################

def descFile_directory_path(instance, filename):
    # 文件上传到MEDIA_ROOT/uploads/project_<name>/<filename>目录中
    return 'downloads/project_【{0}】/网络集成/02-描述配置/{1}'.format(instance.project.name, instance.name)

class DescFile(models.Model):
    def __str__(self):
        return '%s <网络设备描述配置>: %s' % (self.project.name, self.name)

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file = models.FileField(upload_to=descFile_directory_path)

    name = models.CharField(max_length=64)
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')

    class Meta:
        verbose_name = '网络设备描述配置'
        verbose_name_plural = '网络设备描述配置'
        ordering = ['-c_time']

















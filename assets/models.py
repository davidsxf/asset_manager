from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid


class AssetTag(models.Model):
    """资产标签"""
    name = models.CharField('标签名', max_length=50)
    color = models.CharField('颜色', max_length=20, default='is-info')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '资产标签'
        verbose_name_plural = '资产标签'

    def __str__(self):
        return self.name
    

class Asset(models.Model):
    """资产模型"""
    name = models.CharField('资产名称', max_length=100)
    ip_address = models.GenericIPAddressField('IP地址')
    mac_address = models.CharField('MAC地址', max_length=17, blank=True)
    type_choices = (
        ('SERVER', '服务器'),
        ('SWITCH', '交换机'),
        ('ROUTER', '路由器'),
        ('FIREWALL', '防火墙'),
        ('ENDPOINT', '终端设备'),
        ('OTHER', '其他设备'),
    )
    asset_type = models.CharField('资产类型', max_length=20, choices=type_choices)
    model = models.CharField('型号', max_length=100, blank=True)
    manufacturer = models.CharField('制造商', max_length=100, blank=True)
    location = models.CharField('位置', max_length=100)
    department = models.ForeignKey('organization.Department', on_delete=models.PROTECT, verbose_name='所属部门')
    status_choices = (
        ('ACTIVE', '使用中'),
        ('INACTIVE', '闲置'),
        ('MAINTENANCE', '维护中'),
        ('SCRAPPED', '报废'),
    )
    status = models.CharField('状态', max_length=20, choices=status_choices, default='ACTIVE')
    tags = models.ManyToManyField(AssetTag, blank=True, verbose_name='标签')
   # 采购信息
    purchase_date = models.DateField('采购日期', null=True, blank=True)
    purchase_price = models.DecimalField('采购价格', max_digits=10, decimal_places=2, 
                                       null=True, blank=True)
    warranty_expire = models.DateField('保修到期', null=True, blank=True)
    supplier = models.CharField('供应商', max_length=100, blank=True)
    
    # 系统信息
    os = models.CharField('操作系统', max_length=100, blank=True)
    os_version = models.CharField('系统版本', max_length=50, blank=True)
    cpu = models.CharField('CPU', max_length=100, blank=True)
    memory = models.CharField('内存', max_length=50, blank=True)
    disk = models.CharField('硬盘', max_length=100, blank=True)
    
    description = models.TextField('描述', blank=True)
    notes = models.TextField('备注', blank=True)
    
    # 审计字段
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, 
                                 related_name='created_assets',
                                 verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '资产'
        verbose_name_plural = '资产'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} ({self.ip_address})"
        
    def get_absolute_url(self):
        return reverse('assets:detail', kwargs={'pk': self.pk})


class AssetChange(models.Model):
    """资产变更记录"""
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name='资产')
    change_type_choices = (
        ('CREATE', '创建'),
        ('UPDATE', '更新'),
        ('STATUS', '状态变更'),
        ('TRANSFER', '部门转移'),
        ('MAINTENANCE', '维护'),
        ('SCRAP', '报废'),
    )
    change_type = models.CharField('变更类型', max_length=20, choices=change_type_choices)
    description = models.TextField('变更描述')
    changed_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='操作人')
    changed_at = models.DateTimeField('变更时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '资产变更'
        verbose_name_plural = '资产变更'
        ordering = ['-changed_at']

class MaintenanceRecord(models.Model):
    """维护记录"""
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name='资产')
    maintenance_type_choices = (
        ('ROUTINE', '例行维护'),
        ('REPAIR', '故障维修'),
        ('UPGRADE', '升级改造'),
    )
    maintenance_type = models.CharField('维护类型', max_length=20, 
                                      choices=maintenance_type_choices)
    title = models.CharField('标题', max_length=200)
    description = models.TextField('维护内容')
    maintainer = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='维护人')
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间', null=True, blank=True)
    cost = models.DecimalField('维护费用', max_digits=10, decimal_places=2, 
                             null=True, blank=True)
    result = models.TextField('维护结果', blank=True)
    created_at = models.DateTimeField('记录时间', auto_now_add=True)

    class Meta:
        verbose_name = '维护记录'
        verbose_name_plural = '维护记录'
        ordering = ['-start_time']
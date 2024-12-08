from django.db import models
from assets.models import Asset

class Connection(models.Model):
    source = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='source_connections',
                             verbose_name='源设备')
    target = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='target_connections',
                             verbose_name='目标设备')
    connection_type_choices = (
        ('PHYSICAL', '物理连接'),
        ('LOGICAL', '逻辑连接'),
    )
    connection_type = models.CharField('连接类型', max_length=20, choices=connection_type_choices)
    interface_a = models.CharField('源接口', max_length=50, blank=True)
    interface_b = models.CharField('目标接口', max_length=50, blank=True)
    bandwidth = models.CharField('带宽', max_length=50, blank=True)
    vlan = models.CharField('VLAN', max_length=50, blank=True)
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '网络连接'
        verbose_name_plural = '网络连接'
        unique_together = [['source', 'target', 'interface_a', 'interface_b']]
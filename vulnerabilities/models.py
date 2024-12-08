from django.db import models
from assets.models import Asset
from django.contrib.auth.models import User

class Vulnerability(models.Model):
    title = models.CharField('漏洞标题', max_length=200)
    cve_id = models.CharField('CVE编号', max_length=20, blank=True)
    affected_assets = models.ManyToManyField(Asset, verbose_name='受影响资产')
    severity_choices = (
        ('CRITICAL', '严重'),
        ('HIGH', '高危'),
        ('MEDIUM', '中危'),
        ('LOW', '低危'),
    )
    severity = models.CharField('危险等级', max_length=10, choices=severity_choices)
    description = models.TextField('漏洞描述')
    solution = models.TextField('解决方案')
    status_choices = (
        ('OPEN', '未修复'),
        ('IN_PROGRESS', '修复中'),
        ('FIXED', '已修复'),
        ('VERIFIED', '已验证'),
        ('FALSE_POSITIVE', '误报'),
    )
    status = models.CharField('状态', max_length=20, choices=status_choices, default='OPEN')
    discovered_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='discovered_vulnerabilities',
                                    verbose_name='发现人')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='assigned_vulnerabilities', verbose_name='负责人')
    discovered_at = models.DateTimeField('发现时间', auto_now_add=True)
    fixed_at = models.DateTimeField('修复时间', null=True, blank=True)
    verified_at = models.DateTimeField('验证时间', null=True, blank=True)
    notes = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '漏洞'
        verbose_name_plural = '漏洞'
        ordering = ['-discovered_at']
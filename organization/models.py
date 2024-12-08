from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField('部门名称', max_length=50)
    code = models.CharField('部门编码', max_length=20, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              verbose_name='上级部门', related_name='children')
    manager = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True,
                               verbose_name='部门主管', related_name='managed_department')
    description = models.TextField('部门描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门'
        ordering = ['code']

    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户账号')
    employee_id = models.CharField('工号', max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, verbose_name='所属部门')
    position = models.CharField('职位', max_length=50)
    phone = models.CharField('手机号', max_length=11)
    office_phone = models.CharField('办公电话', max_length=20, blank=True)
    email = models.EmailField('邮箱')
    entry_date = models.DateField('入职日期')
    status_choices = (
        ('ACTIVE', '在职'),
        ('LEAVE', '离职'),
        ('SUSPEND', '停职')
    )
    status = models.CharField('在职状态', max_length=10, choices=status_choices, default='ACTIVE')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '职工'
        verbose_name_plural = '职工'
        ordering = ['employee_id']

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"
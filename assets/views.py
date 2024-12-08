from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView,TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import HttpResponse
import csv
import xlsxwriter
from io import BytesIO
from .models import Asset, AssetChange, MaintenanceRecord, AssetTag
from .forms import AssetForm, AssetBulkImportForm, MaintenanceRecordForm

from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum


from django.views.generic.edit import FormView
import pandas as pd



class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'assets/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # 搜索
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(ip_address__icontains=search) |
                Q(asset_number__icontains=search) |
                Q(mac_address__icontains=search)
            )
         # 筛选
        asset_type = self.request.GET.get('type')
        if asset_type:
            queryset = queryset.filter(asset_type=asset_type)
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        department = self.request.GET.get('department')
        if department:
            queryset = queryset.filter(department_id=department)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asset_types'] = Asset.type_choices
        context['asset_status'] = Asset.status_choices
        return context
    

class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = 'assets/asset_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['changes'] = self.object.assetchange_set.all()[:5]
        context['maintenance_records'] = self.object.maintenancerecord_set.all()[:5]
        return context
    
class AssetCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = 'assets/asset_form.html'
    permission_required = 'assets.add_asset'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        # 记录变更
        AssetChange.objects.create(
            asset=self.object,
            change_type='CREATE',
            description='创建资产',
            changed_by=self.request.user
        )
        messages.success(self.request, '资产创建成功！')
        return response
    
class AssetUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = 'assets/asset_form.html'
    permission_required = 'assets.change_asset'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        AssetChange.objects.create(
            asset=self.object,
            change_type='UPDATE',
            description='更新资产信息',
            changed_by=self.request.user
        )
        messages.success(self.request, '资产更新成功！')
        return response

class AssetExportView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'assets.view_asset'
    
    def get(self, request):
        # 创建Excel文件
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        # 写入表头
        headers = ['资产编号', '名称', 'IP地址', 'MAC地址', '资产类型', '状态', 
                  '部门', '位置', '采购日期', '保修到期']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
            
        # 写入数据
        assets = Asset.objects.all()
        for row, asset in enumerate(assets, 1):
            worksheet.write(row, 0, asset.asset_number)
            worksheet.write(row, 1, asset.name)
            worksheet.write(row, 2, asset.ip_address)
            worksheet.write(row, 3, asset.mac_address)
            worksheet.write(row, 4, asset.get_asset_type_display())
            worksheet.write(row, 5, asset.get_status_display())
            worksheet.write(row, 6, asset.department.name)
            worksheet.write(row, 7, asset.location)
            worksheet.write(row, 8, asset.purchase_date.strftime('%Y-%m-%d') 
                          if asset.purchase_date else '')
            worksheet.write(row, 9, asset.warranty_expire.strftime('%Y-%m-%d') 
                          if asset.warranty_expire else '')
            
        workbook.close()
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=assets.xlsx'
        return response



class AssetStatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'assets/statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 按类型统计
        type_stats = Asset.objects.values('asset_type')\
            .annotate(count=Count('id'))\
            .order_by('-count')
            
        # 按状态统计
        status_stats = Asset.objects.values('status')\
            .annotate(count=Count('id'))\
            .order_by('-count')
            
        # 按部门统计
        dept_stats = Asset.objects.values('department__name')\
            .annotate(count=Count('id'))\
            .order_by('-count')
            
        # 月度资产变化趋势
        monthly_stats = Asset.objects.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # 维护记录统计
        maintenance_stats = MaintenanceRecord.objects.values('maintenance_type')\
            .annotate(count=Count('id'), total_cost=Sum('cost'))\
            .order_by('-count')
        
        context.update({
            'type_stats': type_stats,
            'status_stats': status_stats,
            'dept_stats': dept_stats,
            'monthly_stats': monthly_stats,
            'maintenance_stats': maintenance_stats,
        })
        return context
    

#批量导入功能

class AssetBulkImportView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = 'assets/import.html'
    form_class = AssetBulkImportForm
    success_url = reverse_lazy('assets:list')
    permission_required = 'assets.add_asset'

    def form_valid(self, form):
        excel_file = form.cleaned_data['file']
        try:
            df = pd.read_excel(excel_file)
            success_count = 0
            error_records = []
            
            for _, row in df.iterrows():
                try:
                    asset = Asset(
                        name=row['名称'],
                        asset_number=row['资产编号'],
                        ip_address=row['IP地址'],
                        asset_type=row['资产类型'],
                        department_id=row['部门ID'],
                        created_by=self.request.user
                    )
                    asset.full_clean()
                    asset.save()
                    success_count += 1
                except Exception as e:
                    error_records.append({
                        'row': row.to_dict(),
                        'error': str(e)
                    })
            
            messages.success(self.request, 
                           f'成功导入{success_count}条记录，失败{len(error_records)}条')
            
            if error_records:
                self.request.session['import_errors'] = error_records
                
        except Exception as e:
            messages.error(self.request, f'导入失败：{str(e)}')
            
        return super().form_valid(form)
    

#维护记录管理：
class MaintenanceRecordCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceRecord
    form_class = MaintenanceRecordForm
    template_name = 'assets/maintenance_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asset'] = get_object_or_404(Asset, pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        form.instance.asset_id = self.kwargs['pk']
        form.instance.maintainer = self.request.user
        response = super().form_valid(form)
        
        # 更新资产状态
        asset = form.instance.asset
        asset.status = 'MAINTENANCE'
        asset.save()
        
        # 记录变更
        AssetChange.objects.create(
            asset=asset,
            change_type='MAINTENANCE',
            description=f'开始维护：{form.instance.title}',
            changed_by=self.request.user
        )
        
        messages.success(self.request, '维护记录已创建')
        return response

class MaintenanceRecordUpdateView(LoginRequiredMixin, UpdateView):
    model = MaintenanceRecord
    form_class = MaintenanceRecordForm
    template_name = 'assets/maintenance_form.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if form.instance.end_time:
            # 维护完成，更新资产状态
            asset = form.instance.asset
            asset.status = 'ACTIVE'
            asset.save()
            
            AssetChange.objects.create(
                asset=asset,
                change_type='MAINTENANCE',
                description=f'完成维护：{form.instance.title}',
                changed_by=self.request.user
            )
            
        messages.success(self.request, '维护记录已更新')
        return response

#资产标签管理：
class TagListView(LoginRequiredMixin, ListView):
    model = AssetTag
    template_name = 'assets/tag_list.html'
    context_object_name = 'tags'

class TagCreateView(LoginRequiredMixin, CreateView):
    model = AssetTag
    fields = ['name', 'color']
    template_name = 'assets/tag_form.html'
    success_url = reverse_lazy('assets:tag_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, '标签创建成功')
        return response

class AssetTagsUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        asset = get_object_or_404(Asset, pk=pk)
        tag_ids = request.POST.getlist('tags')
        asset.tags.set(tag_ids)
        messages.success(request, '资产标签已更新')
        return redirect('assets:detail', pk=pk)
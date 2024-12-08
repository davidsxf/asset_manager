from django import forms
from .models import Asset, MaintenanceRecord
from django.core.exceptions import ValidationError
import ipaddress

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        exclude = ['created_by', 'created_at', 'updated_at']
        
    def clean_ip_address(self):
        ip = self.cleaned_data.get('ip_address')
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            raise ValidationError('请输入有效的IP地址')
        return ip
        
    def clean_mac_address(self):
        mac = self.cleaned_data.get('mac_address')
        if mac:
            mac = mac.upper()
            if not re.match(r'^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$', mac):
                raise ValidationError('请输入有效的MAC地址')
        return mac

class AssetBulkImportForm(forms.Form):
    file = forms.FileField(label='Excel文件')
    
class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        exclude = ['created_at']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
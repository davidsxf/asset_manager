from rest_framework import serializers
from .models import Asset, MaintenanceRecord, AssetTag

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')

class MaintenanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRecord
        fields = '__all__'
        read_only_fields = ('created_at',)

class AssetTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetTag
        fields = '__all__'
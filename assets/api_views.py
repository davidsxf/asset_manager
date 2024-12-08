from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import AssetSerializer, MaintenanceRecordSerializer, AssetTagSerializer
from .models import Asset, MaintenanceRecord, AssetTag

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def maintenance_history(self, request, pk=None):
        asset = self.get_object()
        maintenance_records = asset.maintenancerecord_set.all()
        serializer = MaintenanceRecordSerializer(maintenance_records, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        total_count = Asset.objects.count()
        type_stats = Asset.objects.values('asset_type')\
            .annotate(count=Count('id'))
        return Response({
            'total_count': total_count,
            'type_statistics': type_stats
        })

class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRecord.objects.all()
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [IsAuthenticated]

class AssetTagViewSet(viewsets.ModelViewSet):
    queryset = AssetTag.objects.all()
    serializer_class = AssetTagSerializer
    permission_classes = [IsAuthenticated] 
from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from assets.api_views import AssetViewSet, MaintenanceRecordViewSet, AssetTagViewSet

router = DefaultRouter()
router.register(r'assets', AssetViewSet)
router.register(r'maintenance', MaintenanceRecordViewSet)
router.register(r'tags', AssetTagViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('assets/', include('assets.urls')),
    path('vulnerabilities/', include('vulnerabilities.urls')),

    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),

]
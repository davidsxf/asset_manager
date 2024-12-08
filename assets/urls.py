from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    path('', views.AssetListView.as_view(), name='list'),
    path('<uuid:pk>/', views.AssetDetailView.as_view(), name='detail'),
    path('create/', views.AssetCreateView.as_view(), name='create'),
    path('<uuid:pk>/update/', views.AssetUpdateView.as_view(), name='update'),
    path('export/', views.AssetExportView.as_view(), name='export'),
    path('import/', views.AssetBulkImportView.as_view(), name='import'),
    path('<uuid:pk>/maintenance/add/', views.MaintenanceRecordCreateView.as_view(), 
         name='add_maintenance'),
]
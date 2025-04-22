from django.urls import path,include
from .views import CrudDatabases,ListBackups,BackupView
from rest_framework import routers
from django.urls import path
from .views import RunBackupAPIView

router = routers.DefaultRouter()
router.register(r"databases", CrudDatabases, "databases")
router.register(r"backups", BackupView, "backups")

urlpatterns = [
    path("backups/<int:id_database>",ListBackups.as_view(),name="backups"),
    path("", include(router.urls)),
    path('api/run_backup/', RunBackupAPIView.as_view(), name='run_backup'),
]


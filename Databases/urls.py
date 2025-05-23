from django.urls import path,include
from .views import CrudDatabases,ListBackups,BackupView
from rest_framework import routers
from django.urls import path
from .views import RunBackupAPIView,download_local_backup

router = routers.DefaultRouter()
router.register(r"databases", CrudDatabases, "databases")
router.register(r"backups", BackupView, "backups")


from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("backups/<int:id_database>",ListBackups.as_view(),name="backups"),
    path("", include(router.urls)),
    path('api/run_backup/', RunBackupAPIView.as_view(), name='run_backup'),
    path('swagger.<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('backups/<int:db_id>/download/',download_local_backup,name='download_local_backup')
]



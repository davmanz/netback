from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from core.auth_views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    logout_view,
)

from core.views import (AreaViewSet, BackupDiffViewSet, BackupViewSet,
                        ClassificationRuleSetViewSet, CountryViewSet,
                        DeviceTypeViewSet, ManufacturerViewSet,
                        NetworkDeviceViewSet, SiteViewSet, UserSystemViewSet,
                        VaultCredentialViewSet, HealthCheckView,
                        bulk_save_classified_hosts, compareBackupsView,
                        compareSpecificBackups, executeCommand,
                        from_csv_bulk_view, from_zabbix_bulk_view,
                        get_backup_schedule, get_last_backups,
                        getBackupHistory, getBackupStatus, ping_device,
                        update_backup_schedule, zabbix_connectivity_status,
                        backupDeviceView,
                        test_csrf_view,
                        )

# Crear el router para la API
router = DefaultRouter()
router.register(r"vaultcredentials", VaultCredentialViewSet)
router.register(r"networkdevice", NetworkDeviceViewSet)
router.register(r"backup", BackupViewSet)
router.register(r"backupdiff", BackupDiffViewSet)
router.register(r"users", UserSystemViewSet)
router.register(r"countries", CountryViewSet, basename="countries")
router.register(r"sites", SiteViewSet, basename="sites")
router.register(r"areas", AreaViewSet, basename="areas")
router.register(r"manufacturers", ManufacturerViewSet)
router.register(r"devicetypes", DeviceTypeViewSet)
router.register(
    r"classification-rules",
    ClassificationRuleSetViewSet,
    basename="classification-rules",
)

# Definir las rutas de la API
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/logout/", logout_view, name="token_logout"),
    path("api/networkdevice/<uuid:pk>/command/", executeCommand, name="executeCommand"),
    path("api/networkdevice/<uuid:pk>/backup/", backupDeviceView, name="backupDevice"),
    path(
        "api/networkdevice/<uuid:pk>/compare/",
        compareBackupsView,
        name="compareBackups",
    ),
    path(
        "api/networkdevice/<uuid:pk>/backups/",
        getBackupHistory,
        name="getBackupHistory",
    ),
    path(
        "api/networkdevice/<uuid:pk>/status/", getBackupStatus, name="getBackupStatus"
    ),
    path(
        "api/networkdevice/bulk/from-zabbix/",
        from_zabbix_bulk_view,
        name="bulk-from-zabbix",
    ),
    path("api/networkdevice/bulk/from-csv/", from_csv_bulk_view, name="bulk-from-csv"),
    path(
        "api/networkdevice/bulk/save/",
        bulk_save_classified_hosts,
        name="bulk-save-classified-hosts",
    ),
    path("api/backups/last/", get_last_backups, name="get_last_backups"),
    path(
        "api/backups/compare/<uuid:backupOldId>/<uuid:backupNewId>/",
        compareSpecificBackups,
        name="compareSpecificBackups",
    ),
    path(
        "api/backup-config/schedule/",
        update_backup_schedule,
        name="update_backup_schedule",
    ),
    path(
        "api/backup-config/schedule/get/",
        get_backup_schedule,
        name="get_backup_schedule",
    ),
    path("api/users/me/", UserSystemViewSet.as_view({"get": "me"}), name="user-me"),
    path("api/zabbix/status/", zabbix_connectivity_status, name="zabbix_status"),
    path("api/ping/", ping_device, name="ping_device"),
    path("api/test-csrf/", test_csrf_view, name="test-csrf"),
    path('api/health/', HealthCheckView.as_view(permission_classes=[AllowAny]), name='health-check'),
]

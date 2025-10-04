import re
import shutil
import subprocess
from datetime import time

from django.utils import timezone
from django.db import IntegrityError
from django.db.models import Max

from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.classification_engine import (HostClassifier, get_hosts_from_csv, get_hosts_from_zabbix)
from utils.env import get_zabbix_token, get_zabbix_url
from utils.zabbix_manager import ZabbixManager

from .models import (Area, Backup, BackupDiff, BackupSchedule, BackupStatus,
                     ClassificationRuleSet, Country, DeviceType, Manufacturer,
                     NetworkDevice, Site, UserSystem, VaultCredential)
from .network_util.backup import backupDevice
from .network_util.comparison import compareBackups
from .network_util.comparison import compareSpecificBackups as specificCompareBackups
from .network_util.executor import executeCommandOnDevice
from .permissions import IsAdmin, IsOperator, IsViewer
from .serializers import (AreaSerializer, BackupDiffSerializer,
                          BackupSerializer, ClassificationRuleSetSerializer,
                          CountrySerializer, DeviceTypeSerializer,
                          ManufacturerSerializer, NetworkDeviceSerializer,
                          SiteSerializer, UserSystemSerializer,
                          VaultCredentialSerializer)
from utils.ping import ping_ip


# **********************************************************
# 👤 Gestión de Usuarios
# **********************************************************
class UserSystemViewSet(viewsets.ModelViewSet):
    """API para gestionar usuarios"""
    queryset = UserSystem.objects.all()
    serializer_class = UserSystemSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "update", "partial_update"]:
            return [IsAuthenticated()]
        elif self.action in ["create", "destroy"]:
            return [IsAdmin()]
        return super().get_permissions()

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Devuelve la información del usuario autenticado"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        user_to_modify = self.get_object()
        if not request.user.role == "admin" and request.user != user_to_modify:
            return Response(
                {"detail": "No tienes permiso para editar este usuario."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        user_to_modify = self.get_object()
        if not request.user.role == "admin" and request.user != user_to_modify:
            return Response(
                {"detail": "No tienes permiso para editar este usuario."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().partial_update(request, *args, **kwargs)


class VaultCredentialViewSet(viewsets.ModelViewSet):
    queryset = VaultCredential.objects.all()
    serializer_class = VaultCredentialSerializer
    permission_classes = [IsOperator]


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all().order_by("name")
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated]


class SiteViewSet(viewsets.ModelViewSet):
    serializer_class = SiteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Permite filtrar sitios por ID de país (?country_id=...)"""
        queryset = Site.objects.select_related("country").all().order_by("name")
        country_id = self.request.query_params.get("country_id")# type: ignore
        if country_id:
            queryset = queryset.filter(country__id=country_id)
        return queryset

# **********************************************************
# 📍 Vista para Áreas
# **********************************************************
class AreaViewSet(viewsets.ModelViewSet):
    """API para gestionar áreas, filtrando por sitio o país"""
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Permite filtrar áreas por sitio o país (?site_id=... o ?country_id=...)"""
        queryset = (
            Area.objects.select_related("site", "site__country").all().order_by("name")
        )
        site_id = self.request.query_params.get("site_id")# type: ignore
        country_id = self.request.query_params.get("country_id")# type: ignore

        if site_id:
            queryset = queryset.filter(site__id=site_id)
        elif country_id:
            queryset = queryset.filter(site__country__id=country_id)

        return queryset


# **********************************************************
# 🔌 Gestión de Equipos
# **********************************************************
class NetworkDeviceViewSet(viewsets.ModelViewSet):
    queryset = NetworkDevice.objects.all()
    serializer_class = NetworkDeviceSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsViewer()]
        elif self.action in ["create"]:
            return [IsOperator()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Valida que solo se use una credencial al crear un equipo"""
        serializer.save()

    def perform_update(self, serializer):
        """Valida que solo se use una credencial al actualizar un equipo"""
        serializer.save()


# **********************************************************
# 📍 Gestión de Fabricantes (Manufacturers)
# **********************************************************
class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all().order_by("name")
    serializer_class = ManufacturerSerializer
    permission_classes = [IsAuthenticated]


# **********************************************************
# 📍 Gestión de Tipos de Equipos (DeviceType)
# **********************************************************
class DeviceTypeViewSet(viewsets.ModelViewSet):
    queryset = DeviceType.objects.all().order_by("name")
    serializer_class = DeviceTypeSerializer
    permission_classes = [IsAuthenticated]


# **********************************************************
# 📂 Gestión de Backups
# **********************************************************
class BackupViewSet(viewsets.ModelViewSet):
    queryset = Backup.objects.all()
    serializer_class = BackupSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsViewer()]
        elif self.action in ["create"]:
            return [IsOperator()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAdmin()]
        return super().get_permissions()


class BackupDiffViewSet(viewsets.ModelViewSet):
    queryset = BackupDiff.objects.all()
    serializer_class = BackupDiffSerializer
    permission_classes = [IsAuthenticated]


# **********************************************************
# 📂 Clasificación de Dispositivos
# **********************************************************
class ClassificationRuleSetViewSet(viewsets.ModelViewSet):
    queryset = ClassificationRuleSet.objects.all().order_by("-createdAt")
    serializer_class = ClassificationRuleSetSerializer
    permission_classes = [IsAdmin]

# **********************************************************
# 🏥 Vista de Salud del Backend
# **********************************************************
class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Ruta de salud simple para verificar si el backend está funcionando.
        """
        try:
            return Response({
                "status": "ok",
                "message": "Backend is up and running!",
                "timestamp": timezone.now().isoformat()
            })
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=500)


##FUNCIONES
# **********************************************************
# 📊 Estado de Backups
# **********************************************************
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getBackupStatus(request, pk):
    """Obtener el estado de los respaldos del dispositivo"""
    try:
        device = NetworkDevice.objects.get(pk=pk)
        statuses = BackupStatus.objects.filter(device=device).order_by("-timestamp")
        data = [
            {"status": s.status, "message": s.message, "backupTime": s.timestamp}
            for s in statuses
        ]
        return Response({"device": device.hostname, "statuses": data})
    except NetworkDevice.DoesNotExist:
        return Response({"error": "Device not found"}, status=404)


# **********************************************************
# 📊 Comparación de Backups
# **********************************************************
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_last_backups(request):
    """Obtener el último respaldo de cada dispositivo de red, incluyendo el id del backup."""
    # Obtenemos, para cada dispositivo, la fecha máxima de respaldo.
    latest_backups = Backup.objects.values("device_id").annotate(
        last_backup=Max("backupTime")
    )
    devices_with_backup = []

    for backup in latest_backups:
        # Obtenemos el dispositivo correspondiente.
        device = NetworkDevice.objects.get(id=backup["device_id"])
        # Buscamos el backup que tenga la fecha máxima registrada.
        latest_backup_obj = Backup.objects.get(
            device_id=backup["device_id"], backupTime=backup["last_backup"]
        )
        devices_with_backup.append(
            {
                "id": device.id,
                "hostname": device.hostname,
                "ipAddress": device.ipAddress,
                "lastBackup": backup["last_backup"],
                "backup_id": latest_backup_obj.id,
            }
        )
    return Response(devices_with_backup)


# **********************************************************
# 📊 Obtener historial de backups
# **********************************************************
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getBackupHistory(request, pk):
    """Obtener historial de respaldos de un dispositivo."""
    try:
        device = NetworkDevice.objects.get(pk=pk)
        backups = Backup.objects.filter(device=device).order_by("backupTime")
        data = [
            {"id": backup.id, "backupTime": backup.backupTime} for backup in backups
        ]
        return Response(data)
    except NetworkDevice.DoesNotExist:
        return Response({"error": "Device not found"}, status=404)


# **********************************************************
# 📂 Respaldo de Dispositivos
# **********************************************************
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def backupDeviceView(request, pk):
    """Realizar un respaldo de un dispositivo."""
    try:
        device = NetworkDevice.objects.get(pk=pk)
        result = backupDevice(device)
        return Response(result)
    except NetworkDevice.DoesNotExist:
        return Response({"error": "Device not found"}, status=404)


# **********************************************************
### Comparación de Backups
# **********************************************************
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def compareBackupsView(request, pk):
    """Comparar los dos últimos respaldos de un dispositivo."""
    try:
        device = NetworkDevice.objects.get(pk=pk)
        result = compareBackups(device)

        # Evitar KeyError si result no contiene las claves esperadas
        try:
            succ = result.get("success")
            bdid = result.get("backupDiffId")
            changes = result.get("changes")
            print(f'success {succ} backupDiffId {bdid} changes {changes}')
        except Exception:
            print("compareBackups returned unexpected structure: %r" % (result,))

        if "error" in result:
            return Response(result, status=400)

        return Response(
            {
                "success": result["success"],
                "backupDiffId": result["backupDiffId"],
                "changes": result["changes"],
            }
        )
    except NetworkDevice.DoesNotExist:
        return Response({"error": "Device not found"}, status=404)


# **********************************************************
# Comparación de Backups Específicos
# **********************************************************
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def compareSpecificBackups(request, backupOldId, backupNewId):
    """Comparar dos respaldos específicos del mismo dispositivo asegurando el orden correcto."""
    try:
        backup1 = Backup.objects.get(id=backupOldId)
        backup2 = Backup.objects.get(id=backupNewId)

        # Validar que ambos backups pertenecen al mismo dispositivo
        if backup1.device.id != backup2.device.id:
            return Response(
                {
                    "success": False,
                    "error": "Ambos backups deben pertenecer al mismo dispositivo",
                },
                status=400,
            )

        # Ordenar los backups por su fecha
        backupOld, backupNew = (
            (backup2, backup1)
            if backup1.backupTime > backup2.backupTime
            else (backup1, backup2)
        )

        # Ejecutar la comparación
        result = specificCompareBackups(backupOld, backupNew)

        # ✅ Validar que result tenga "success"
        if not isinstance(result, dict) or "success" not in result:
            return Response(
                {"success": False, "error": "Error desconocido al comparar backups"},
                status=500,
            )

        # ✅ Si la comparación falló, devolver error
        if not result["success"]:
            return Response(result, status=400)

        # ✅ Validar `backupDiffId` antes de acceder a él
        backup_diff_id = result.get("backupDiffId")
        if not backup_diff_id:
            return Response(
                {"success": False, "error": "Error al generar backupDiffId"}, status=500
            )

        # ✅ Devolver la respuesta correcta
        return Response(
            {
                "success": True,
                "backupDiffId": backup_diff_id,
                "changes": result["changes"],
            }
        )

    except Backup.DoesNotExist:
        return Response(
            {"success": False, "error": "Uno o ambos backups no fueron encontrados"},
            status=404,
        )


# **********************************************************
# 💻 Comandos y Diagnóstico
# **********************************************************
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def executeCommand(request, pk):
    """Ejecutar un comando en el dispositivo"""
    try:
        device = NetworkDevice.objects.get(pk=pk)
        command = request.data.get("command")
        if not command:
            return Response({"error": "Command is required"}, status=400)
        result = executeCommandOnDevice(device, command)
        return Response({"result": result})
    except NetworkDevice.DoesNotExist:
        return Response({"error": "Device not found"}, status=404)


# **********************************************************
# Ping a Dispositivo
# **********************************************************
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ping_device(request):
    """Ejecuta un ping a un dispositivo desde el servidor"""
    ip = request.data.get("ip")

    if not ip:
        return Response({"status": "error", "message": "Debes proporcionar una dirección IP válida."}, status=400)

    try:
        ping_result = ping_ip(ip)

        if ping_result.get("reachable"):
            return Response({
                "status": "success",
                "data": {
                    "ip": ip,
                    "reachable": True,
                    "message": "✅ Dispositivo activo",
                    "stats": ping_result.get("stats", {}),
                }
            })

        # No reachable -> map error codes to messages expected by frontend
        error = ping_result.get("error")
        message = "❌ No se pudo alcanzar el dispositivo"
        if error == "unknown_host":
            message = "❌ Host desconocido"
        elif error == "network_unreachable":
            message = "❌ Red inalcanzable"
        elif error == "timeout":
            return Response({"status": "error", "message": "⌛ Tiempo de espera agotado al intentar alcanzar el dispositivo"}, status=408)

        return Response({"status": "error", "data": {"ip": ip, "reachable": False, "message": message}})

    except Exception as e:
        return Response({"status": "error", "message": f"⚠ Error al ejecutar ping: {str(e)}"}, status=500)


# **********************************************************
# 💻 Gestion de Celery (Automatisacion de respaldos)
# **********************************************************
@api_view(["POST"])
@permission_classes([IsAdmin])
def update_backup_schedule(request):

    new_time = request.data.get("scheduled_time")
    if not new_time:
        return Response(
            {"error": "Debes proporcionar una hora en formato HH:MM."}, status=400
        )

    try:
        # Convertir a formato TimeField
        hours, minutes = map(int, new_time.split(":"))
        scheduled_time = time(hours, minutes)

        # Buscar si ya existe un registro, si no, crearlo con UUID
        schedule, created = BackupSchedule.objects.get_or_create(
            defaults={"scheduled_time": scheduled_time}  # Evita el error de NULL
        )

        # Si ya existía, actualiza la hora
        if not created:
            schedule.scheduled_time = scheduled_time
            schedule.save()

        return Response(
            {
                "success": True,
                "message": f"Respaldo programado a las {scheduled_time}",
                "schedule_id": str(schedule.id),  # Devolver el UUID
            }
        )
    except ValueError:
        return Response(
            {"error": "Formato de hora inválido. Usa HH:MM (24h)."}, status=400
        )


# **********************************************************
# Obtener la hora programada del respaldo automático
# **********************************************************
@api_view(["GET"])
@permission_classes([IsAdmin])
def get_backup_schedule(request):
    """Obtener la hora programada del respaldo automático"""
    try:
        schedule = BackupSchedule.objects.first()  # Obtener el primer registro
        if schedule:
            return Response(
                {"scheduled_time": schedule.scheduled_time.strftime("%H:%M")}
            )
        return Response({"scheduled_time": None}, status=404)
    except Exception as e:
        return Response({"error": f"Error al obtener la hora: {str(e)}"}, status=500)


# **********************************************************
# Estado de Conectividad con Zabbix
# **********************************************************
@api_view(["GET"])
@permission_classes([IsAdmin])
def zabbix_connectivity_status(request):
    zabbix_host = (
        get_zabbix_url().replace("https://", "").replace("http://", "").split("/")[0]
    )

    # Ejecutar ping
    ping_proc = subprocess.run(
        ["ping", "-c", "2", zabbix_host], capture_output=True, text=True
    )
    ping_output = ping_proc.stdout
    pass_packets = ping_output.count("bytes from")
    drop_packets = 2 - pass_packets

    # Evaluar si intentar conexión con Zabbix
    activate = False
    zabbix_api_status = "skipped"
    connect_attempted = False

    if pass_packets > 0:
        connect_attempted = True
        try:
            zm = ZabbixManager(url=get_zabbix_url(), token=get_zabbix_token())
            activate = zm.connect()
            zabbix_api_status = "ok" if activate else "error"
        except Exception as e:
            print(f"❌ Error al conectar con Zabbix: {e}")
            zabbix_api_status = "error"

    return Response(
        {
            "activate": activate,
            "zabbix_api_status": zabbix_api_status,
            "connect_attempted": connect_attempted,
            "ping": {"drop": drop_packets, "pass": pass_packets}
        }
    )

# **********************************************************
# Clasificación de Hosts desde Zabbix
# **********************************************************
@api_view(["POST"])
@permission_classes([IsAdmin])
def from_zabbix_bulk_view(request):
    """
    Clasifica hosts directamente obtenidos desde Zabbix usando un conjunto de reglas.
    Agrega el ID de area, vaultCredential, manufacturer y deviceType con estructura ordenada.
    """
    rule_set_id = request.data.get("ruleSetId")
    if not rule_set_id:
        return Response(
            {"detail": "Falta 'ruleSetId' en el cuerpo de la solicitud."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        rule_set = ClassificationRuleSet.objects.get(id=rule_set_id)
    except ClassificationRuleSet.DoesNotExist:
        return Response(
            {"detail": "El conjunto de reglas no existe."},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        hosts = get_hosts_from_zabbix()
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    classifier = HostClassifier(rule_set.rules)
    classified = classifier.classify_all(hosts)

    for host in classified:
        # Vault Credential
        host["vaultCredential"] = (
            str(rule_set.vaultCredential.id) if rule_set.vaultCredential else None
        )

        # Manufacturer
        name_manufacturer = host.get("manufacturer", "Desconocido")
        manufacturer_obj = Manufacturer.objects.filter(
            name__iexact=name_manufacturer
        ).first()
        host["manufacturer"] = {
            "id": str(manufacturer_obj.id) if manufacturer_obj else None,
            "name": name_manufacturer,
        }

        # Device Type
        name_device_type = host.get("deviceType", "Desconocido")
        device_type_obj = DeviceType.objects.filter(
            name__iexact=name_device_type
        ).first()
        host["deviceType"] = {
            "id": str(device_type_obj.id) if device_type_obj else None,
            "name": name_device_type,
        }

    return Response(classified, status=status.HTTP_200_OK)


# **********************************************************
# Clasificación de Hosts desde CSV
# **********************************************************
@api_view(["POST"])
@permission_classes([IsAdmin])
def from_csv_bulk_view(request):
    """
    Clasifica hosts subidos vía archivo CSV usando un conjunto de reglas.
    """
    rule_set_id = request.data.get("ruleSetId")
    csv_file = request.FILES.get("file")

    if not rule_set_id:
        return Response(
            {"detail": "Falta 'ruleSetId'."}, status=status.HTTP_400_BAD_REQUEST
        )

    if not csv_file:
        return Response(
            {"detail": "Debe subir un archivo CSV en el campo 'file'."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        rule_set = ClassificationRuleSet.objects.get(id=rule_set_id)
    except ClassificationRuleSet.DoesNotExist:
        return Response(
            {"detail": "El conjunto de reglas no existe."},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        hosts = get_hosts_from_csv(csv_file)
    except Exception as e:
        return Response(
            {"detail": f"Error procesando CSV: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    classifier = HostClassifier(rule_set.rules)
    classified = classifier.classify_all(hosts)

    return Response(classified, status=status.HTTP_200_OK)


# **********************************************************
# Salvar Host clasificados
# **********************************************************
@api_view(["POST"])
@permission_classes([IsOperator])
def bulk_save_classified_hosts(request):
    """
    Guarda múltiples hosts clasificados como NetworkDevice en la base de datos.
    """
    hosts_data = request.data.get("hosts", [])
    created = 0
    errors = []

    for idx, host in enumerate(hosts_data):
        # Prepare related objects lookup
        manufacturer = Manufacturer.objects.filter(id=host.get("manufacturer")).first()
        device_type = DeviceType.objects.filter(id=host.get("deviceType")).first()
        area = Area.objects.filter(id=host.get("area")).first()
        vault = (
            VaultCredential.objects.filter(id=host.get("vaultCredential")).first()
            if host.get("vaultCredential")
            else None
        )

        data = {
            "hostname": host.get("hostname"),
            "ipAddress": host.get("ipAddress"),
            "model": host.get("model"),
            "manufacturer": manufacturer.id if manufacturer else host.get("manufacturer"),
            "deviceType": device_type.id if device_type else host.get("deviceType"),
            "area": area.id if area else host.get("area"),
            "vaultCredential": vault.id if vault else host.get("vaultCredential"),
            "customUser": host.get("customUser"),
            "customPass": host.get("customPass"),
        }

        serializer = NetworkDeviceSerializer(data=data)
        if not serializer.is_valid():
            errors.append({"index": idx, "hostname": host.get("hostname"), "errors": serializer.errors})
            continue

        try:
            serializer.save()
            created += 1
        except IntegrityError as e:
            errors.append({"index": idx, "hostname": host.get("hostname"), "error": str(e)})

    return Response(
        {"created": created, "errors": errors},
        status=status.HTTP_201_CREATED if created > 0 else status.HTTP_400_BAD_REQUEST,
    )


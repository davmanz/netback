from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from .models import (Area, Backup, BackupDiff, BackupStatusTracker,
                     ClassificationRuleSet, Country, DeviceType, Manufacturer,
                     NetworkDevice, Site, UserSystem, VaultCredential)


# **********************************************************
# 📍 Serializador de Usuarios
# **********************************************************
class UserSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSystem
        fields = [
            "id",
            "username",
            "email",
            "password",
            "role",
            "is_active",
            "createdAt",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Crea un usuario con la contraseña hasheada"""
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Permite actualización con cambio de contraseña opcional"""
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
        return super().update(instance, validated_data)


# **********************************************************
# 📍 Serializador de Usuarios Vault
# **********************************************************
class VaultCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaultCredential
        fields = "__all__"


# **********************************************************
# 📂 Serializador de Backups
# **********************************************************
class BackupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Backup
        fields = "__all__"


# **********************************************************
# 📂 Serializador de Comparaciones de Backups (BackupDiff)
# **********************************************************
class BackupDiffSerializer(serializers.ModelSerializer):
    structured_changes = serializers.JSONField()  # ✅ Comparación estructurada

    class Meta:
        model = BackupDiff
        fields = [
            "id",
            "device",
            "backupOld",
            "backupNew",
            "changes",
            "structured_changes",
            "createdAt",
        ]


# **********************************************************
# Contador de Intentos de Backups
# **********************************************************
class BackupStatusTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackupStatusTracker
        fields = [
            "success_count",
            "no_change_count",
            "error_count",
            "last_status",
            "last_attempt_time",
        ]


# **********************************************************
# 📍 Serializador de Equipos de Red
# **********************************************************
class NetworkDeviceSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.CharField(source="manufacturer.name", read_only=True)
    device_type_name = serializers.CharField(source="deviceType.name", read_only=True)
    site_name = serializers.CharField(source="area.site.name", read_only=True)
    country_name = serializers.CharField(source="area.site.country.name", read_only=True)
    area_name = serializers.CharField(source="area.name", read_only=True)
    backup_tracker = BackupStatusTrackerSerializer(read_only=True)

    class Meta:
        model = NetworkDevice
        fields = [
            "id", "hostname", "ipAddress", "model", "manufacturer", "manufacturer_name",
            "deviceType", "device_type_name", "site_name", "country_name", "area", "area_name",
            "vaultCredential", "customUser", "customPass", "status",
            "createdAt", "updatedAt", "backup_tracker",
        ]

    def validate(self, data):
        if data.get("vaultCredential") and (data.get("customUser") or data.get("customPass")):
            raise serializers.ValidationError("No puedes usar credenciales propias y Vault al mismo tiempo.")
        return data


# **********************************************************
# 📍 Serializador de Fabricantes (Manufacturer)
# **********************************************************
class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ["id", "name", "get_running_config", "get_vlan_info"]


# **********************************************************
# 📍 Serializador de Tipos de Equipos (DeviceType)
# **********************************************************
class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = ["id", "name"]


# **********************************************************
# 📍 Serializador de Países
# **********************************************************
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name"]


# **********************************************************
# 📍 Serializador de Sitios
# **********************************************************
class SiteSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source="country.name", read_only=True)

    class Meta:
        model = Site
        fields = ["id", "name", "country", "country_name"]

    def validate(self, data):
        """Validar que el país exista antes de asociarlo a un sitio."""
        if not Country.objects.filter(id=data.get("country").id).exists():
            raise serializers.ValidationError("El país seleccionado no existe.")
        return data


# **********************************************************
# 📍 Serializador de Áreas
# **********************************************************
class AreaSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source="site.name", read_only=True)
    country_name = serializers.CharField(source="site.country.name", read_only=True)

    class Meta:
        model = Area
        fields = ["id", "name", "site", "site_name", "country_name"]

    def validate(self, data):
        """Validar que el sitio exista antes de asociarlo a un área."""
        if not Site.objects.filter(id=data.get("site").id).exists():
            raise serializers.ValidationError("El sitio seleccionado no existe.")
        return data


# **********************************************************
# 📂 Serializador de Conjuntos de Reglas de Clasificación
# **********************************************************
class ClassificationRuleSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassificationRuleSet
        fields = ["id", "name", "rules", "vaultCredential", "createdAt"]

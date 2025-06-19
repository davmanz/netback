# from django.contrib.auth.hashers import make_password, check_password
import uuid
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,PermissionsMixin)
from django.db import models
from utils.env import get_encryption_cipher

# **********************************************************
# 📍 Modelo de País
# **********************************************************
class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# **********************************************************
# 📍 Modelo de Sitios
# **********************************************************
class Site(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="sites")

    def __str__(self):
        return f"({self.country.name}) {self.name}"


# **********************************************************
# 📍 Modelo de Áreas
# **********************************************************
class Area(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="areas")

    def __str__(self):
        return f"({self.site.country.name}) {self.site.name} - {self.name} "


# Manager personalizado para manejar la autenticación
class UserSystemManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError("El usuario debe tener un email")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)  # Encripta la contraseña
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.role = "admin"
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


# Modelo de usuario personalizado
class UserSystem(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    role = models.CharField(
        max_length=50,
        choices=[("admin", "Admin"), ("viewer", "Viewer"), ("operator", "Operator")],
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserSystemManager()

    def __str__(self):
        return self.username


# **********************************************************
# 📍Gestion de Vault Credenciales
# **********************************************************
class VaultCredential(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nick = models.CharField(
        max_length=100, unique=True)
    username = models.CharField(max_length=100)
    password = models.TextField()

    @staticmethod
    def _get_cipher():
        return get_encryption_cipher()

    def save(self, *args, **kwargs):
        """Cifra la contraseña antes de guardarla en la base de datos"""
        if self.password and not self.password.startswith("gAAAAA"):
            cipher = self._get_cipher()
            self.password = cipher.encrypt(self.password.encode()).decode()
        super().save(*args, **kwargs)

    def get_plain_password(self):
        """Descifra la contraseña cuando se necesite"""
        if self.password:
            cipher = self._get_cipher()
            return cipher.decrypt(self.password.encode()).decode()
        return None

    def __str__(self):
        return "User = " + self.username + " Nick = " + self.nick


# **********************************************************
# 🔌 Gestión de Dispositivos
# **********************************************************
class Manufacturer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    get_running_config = models.CharField(max_length=100)
    get_vlan_info = models.CharField(max_length=100)
    netmiko_type = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Tipo de dispositivo compatible con Netmiko",
    )

    def __str__(self):
        return self.name


class DeviceType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class NetworkDevice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostname = models.CharField(max_length=50, unique=True)
    ipAddress = models.GenericIPAddressField(unique=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    deviceType = models.ForeignKey(DeviceType, on_delete=models.CASCADE)
    vaultCredential = models.ForeignKey(VaultCredential, on_delete=models.SET_NULL, null=True, blank=True)
    customUser = models.CharField(max_length=100, null=True, blank=True)
    customPass = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)

    def get_commands(self):
        return {
            "runningConfig": self.manufacturer.get_running_config,
            "vlanBrief": self.manufacturer.get_vlan_info,
        }

    def save(self, *args, **kwargs):
        if self.vaultCredential and (self.customUser or self.customPass):
            raise ValueError("No puedes usar credenciales propias y Vault al mismo tiempo.")

        # Si se usan credenciales de Vault, limpiar las credenciales personalizadas
        if self.vaultCredential:
            self.customUser = None
            self.customPass = None

        # Si se usan credenciales personalizadas, eliminar el VaultCredential
        if self.customUser or self.customPass:
            self.vaultCredential = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.hostname} ({self.ipAddress})"



# **********************************************************
# 📂 Gestión de Backups
# **********************************************************
class Backup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(NetworkDevice, on_delete=models.CASCADE)
    backupTime = models.DateTimeField(auto_now_add=True)
    runningConfig = models.TextField()
    vlanBrief = models.TextField()
    checksum = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"Backup {self.device.hostname} - {self.backupTime}"


class BackupDiff(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey("NetworkDevice", on_delete=models.CASCADE)
    backupOld = models.ForeignKey(
        "Backup", related_name="old_backup", on_delete=models.CASCADE
    )
    backupNew = models.ForeignKey(
        "Backup", related_name="new_backup", on_delete=models.CASCADE
    )
    changes = models.TextField()
    structured_changes = models.JSONField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diff for {self.device.hostname} ({self.createdAt})"


class BackupStatus(models.Model):
    device = models.ForeignKey(NetworkDevice, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
    )
    message = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


# **********************************************************
# 📂 Autoamtizacion de Respaldos
# **********************************************************from django.db import models
class BackupSchedule(models.Model):
    """Modelo para definir la hora del respaldo automático"""

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )  # Ahora usa UUID
    scheduled_time = models.TimeField(
        help_text="Hora programada para el respaldo automático"
    )

    def __str__(self):
        return f"Backup programado a las {self.scheduled_time}"


# **********************************************************
# 📂 Clasificación de Dispositivos
# **********************************************************
class ClassificationRuleSet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    rules = models.JSONField(
        help_text="Conjunto de reglas por campo: country, site, area, model, deviceType, manufacturer"
    )
    vaultCredential = models.ForeignKey(
        VaultCredential, on_delete=models.SET_NULL, null=True, blank=True
    )
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# **********************************************************
# 📊 Seguimiento de estados de respaldo por dispositivo
# **********************************************************
class BackupStatusTracker(models.Model):
    STATUS_CHOICES = [
        ("success", "Éxito con cambios"),
        ("unchanged", "Éxito sin cambios"),
        ("error", "Error de red o conexión"),
    ]

    device = models.OneToOneField(
        "NetworkDevice", on_delete=models.CASCADE, related_name="backup_tracker"
    )
    success_count = models.PositiveIntegerField(default=0)
    no_change_count = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    last_attempt_time = models.DateTimeField(auto_now=True)
    last_status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default="error"
    )

    def __str__(self):
        return f"Tracker for {self.device.hostname}"

from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from datetime import time as dtime
from cryptography.fernet import Fernet

from core.models import (
    Country,
    Site,
    Area,
    Manufacturer,
    DeviceType,
    VaultCredential,
    UserSystem,
    NetworkDevice,
    Backup,
    BackupDiff,
    BackupStatus,
    BackupSchedule,
    ClassificationRuleSet,
    BackupStatusTracker,
)


class ModelsCrudTests(TestCase):
    def test_country_crud_and_unique(self):
        c = Country.objects.create(name="TestCountry")
        self.assertIsNotNone(c.id)

        got = Country.objects.get(pk=c.id)
        self.assertEqual(got.name, "TestCountry")

        got.name = "TestCountry2"
        got.save()
        self.assertEqual(Country.objects.get(pk=c.id).name, "TestCountry2")

        # unique constraint (use atomic savepoint so DB isn't left broken)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Country.objects.create(name="TestCountry2")

        got.delete()
        with self.assertRaises(Country.DoesNotExist):
            Country.objects.get(pk=c.id)

    def test_site_area_crud_and_cascade(self):
        c = Country.objects.create(name="C1")
        s = Site.objects.create(name="S1", country=c)
        self.assertEqual(s.country.id, c.id)

        a = Area.objects.create(name="A1", site=s)
        self.assertEqual(a.site.id, s.id)

        # delete country cascades to site and area
        c.delete()
        self.assertEqual(Site.objects.filter(pk=s.id).count(), 0)
        self.assertEqual(Area.objects.filter(pk=a.id).count(), 0)

    def test_manufacturer_and_devicetype(self):
        m = Manufacturer.objects.create(name="M1", get_running_config="show run", get_vlan_info="show vlan")
        dt = DeviceType.objects.create(name="DT1")
        self.assertEqual(m.name, "M1")
        self.assertEqual(dt.name, "DT1")

        # netmiko_type validation
        from core.models import SUPPORTED_NETMIKO_TYPES
        m.netmiko_type = "invalid_type"
        with self.assertRaises(ValidationError):
            m.full_clean()

    def test_vaultcredential_encryption_and_plain(self):
        key = Fernet.generate_key().decode()
        with override_settings(ENCRYPTION_KEY_VAULT=key):
            vc = VaultCredential(nick="v1", username="u1", password="secret_pass")
            vc.save()
            # stored password should not equal plain
            self.assertNotEqual(vc.password, "secret_pass")
            plain = vc.get_plain_password()
            self.assertEqual(plain, "secret_pass")

        # without key, save should raise
        vc2 = VaultCredential(nick="v2", username="u2", password="p")
        with override_settings(ENCRYPTION_KEY_VAULT=None):
            with self.assertRaises(RuntimeError):
                vc2.save()

    def test_user_system_manager_and_password(self):
        u = UserSystem.objects.create_user(username="u1", email="u1@test", password="pwd")
        self.assertTrue(u.check_password("pwd"))
        su = UserSystem.objects.create_superuser(username="admin1", email="a@a", password="pwd")
        self.assertTrue(su.is_superuser)
        self.assertTrue(su.is_staff)

    def test_networkdevice_crud_variants(self):
        # Setup related
        m = Manufacturer.objects.create(name="M1", get_running_config="show run", get_vlan_info="show vlan")
        dt = DeviceType.objects.create(name="DT1")
        c = Country.objects.create(name="CC")
        s = Site.objects.create(name="SS", country=c)
        a = Area.objects.create(name="AA", site=s)

        # Vault credential path
        key = Fernet.generate_key().decode()
        with override_settings(ENCRYPTION_KEY_VAULT=key):
            vc = VaultCredential.objects.create(nick="v1", username="vuser", password="vpass")
            nd = NetworkDevice.objects.create(hostname="h1", ipAddress="10.0.0.1", model="mod", manufacturer=m, deviceType=dt, vaultCredential=vc, area=a)
            self.assertIsNotNone(nd.id)
            self.assertIsNone(nd.customUser)

        # custom credentials path
        nd2 = NetworkDevice.objects.create(hostname="h2", ipAddress="10.0.0.2", model="mod2", manufacturer=m, deviceType=dt, customUser="u", customPass="p", area=a)
        self.assertIsNotNone(nd2.id)
        # ensure vaultCredential cleared when custom provided
        self.assertIsNone(nd2.vaultCredential)

    def test_backup_and_constraints(self):
        # Setup minimal device
        m = Manufacturer.objects.create(name="M2", get_running_config="r", get_vlan_info="v")
        dt = DeviceType.objects.create(name="DT2")
        c = Country.objects.create(name="Cz")
        s = Site.objects.create(name="Sx", country=c)
        a = Area.objects.create(name="Ax", site=s)
        nd = NetworkDevice.objects.create(hostname="hb", ipAddress="10.0.0.10", model="m", manufacturer=m, deviceType=dt, customUser="u", customPass="p", area=a)

        b1 = Backup.objects.create(device=nd, runningConfig="r1", vlanBrief="v1", checksum="abc123")
        self.assertIsNotNone(b1.id)

        # unique_together: same device and checksum should raise (atomic savepoint)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Backup.objects.create(device=nd, runningConfig="r2", vlanBrief="v2", checksum="abc123")

        # BackupDiff
        b2 = Backup.objects.create(device=nd, runningConfig="r3", vlanBrief="v3", checksum="def456")
        bd = BackupDiff.objects.create(device=nd, backupOld=b1, backupNew=b2, changes="chg")
        self.assertIsNotNone(bd.id)

    def test_backupstatus_and_tracker_and_schedule_and_ruleset(self):
        # minimal setup
        m = Manufacturer.objects.create(name="M3", get_running_config="r", get_vlan_info="v")
        dt = DeviceType.objects.create(name="DT3")
        c = Country.objects.create(name="Cq")
        s = Site.objects.create(name="Sq", country=c)
        a = Area.objects.create(name="Aq", site=s)
        nd = NetworkDevice.objects.create(hostname="hn", ipAddress="10.0.0.20", model="m", manufacturer=m, deviceType=dt, customUser="u", customPass="p", area=a)

        bs = BackupStatus.objects.create(device=nd, status="pending", message="ok")
        self.assertIsNotNone(bs.pk)

        tracker = BackupStatusTracker.objects.create(device=nd)
        self.assertEqual(tracker.success_count, 0)

        schedule = BackupSchedule.objects.create(scheduled_time=dtime(hour=4, minute=0))
        self.assertIsNotNone(schedule.id)

        rules = ClassificationRuleSet.objects.create(name="rs1", rules={"country": "C"})
        self.assertIsNotNone(rules.id)
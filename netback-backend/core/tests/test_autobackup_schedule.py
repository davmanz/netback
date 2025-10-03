from django.test import TestCase, override_settings
from django.core.management import call_command
from django.utils import timezone
from datetime import time

from django_celery_beat.models import CrontabSchedule, PeriodicTask

from core.models import BackupSchedule


class AutoBackupScheduleTests(TestCase):
    def test_management_command_creates_crontab_and_periodictask(self):
        # Run management command for 02:30 UTC
        call_command("create_autobackup_periodic", "--hour", "2", "--minute", "30", "--timezone", "UTC")

        # Check that CrontabSchedule exists
        cs = CrontabSchedule.objects.filter(minute="30", hour="2", timezone="UTC").first()
        self.assertIsNotNone(cs, "CrontabSchedule not created by command")

        # Check that PeriodicTask exists and references the crontab
        pt = PeriodicTask.objects.filter(name="autoBackup").first()
        self.assertIsNotNone(pt, "PeriodicTask 'autoBackup' not created")
        self.assertIsNotNone(pt.crontab)
        self.assertEqual(pt.crontab.id, cs.id)

    def test_signal_creates_periodictask_on_backupschedule_save_and_disables_on_delete(self):
        # Create a BackupSchedule at 04:15
        bs = BackupSchedule.objects.create(scheduled_time=time(hour=4, minute=15))

        # After save the signal should have created the CrontabSchedule and PeriodicTask
        cs = CrontabSchedule.objects.filter(minute="15", hour="4").first()
        self.assertIsNotNone(cs, "CrontabSchedule not created by signal")

        pt = PeriodicTask.objects.filter(name="autoBackup").first()
        self.assertIsNotNone(pt, "PeriodicTask not created by signal")
        self.assertTrue(pt.enabled)

        # Now delete the BackupSchedule -> signal should disable the PeriodicTask
        bs.delete()
        pt.refresh_from_db()
        self.assertFalse(pt.enabled, "PeriodicTask should be disabled after BackupSchedule deletion")

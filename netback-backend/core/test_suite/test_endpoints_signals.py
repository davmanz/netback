from unittest.mock import patch, Mock

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory, force_authenticate

from core.models import (
	Manufacturer, DeviceType, Country, Site, Area, VaultCredential,
	NetworkDevice, ClassificationRuleSet, UserSystem
)
from core.views import executeCommand, bulk_save_classified_hosts, from_csv_bulk_view, zabbix_connectivity_status


class EndpointsSignalsTests(TestCase):
	def setUp(self):
		self.factory = APIRequestFactory()
		# create users with roles
		self.admin = UserSystem.objects.create_user(username="admin", email="a@a", password="p")
		self.admin.role = "admin"
		self.admin.save()

		self.operator = UserSystem.objects.create_user(username="op", email="o@o", password="p")
		self.operator.role = "operator"
		self.operator.save()

	@patch("core.views.executeCommandOnDevice")
	def test_execute_command_endpoint(self, mock_exec):
		mock_exec.return_value = {"output": "ok"}
		m = Manufacturer.objects.create(name="M1", get_running_config="cmd", get_vlan_info="v")
		dt = DeviceType.objects.create(name="DT1")
		c = Country.objects.create(name="Cx")
		s = Site.objects.create(name="Sx", country=c)
		a = Area.objects.create(name="Ax", site=s)
		nd = NetworkDevice.objects.create(hostname="hcmd", ipAddress="10.0.0.9", manufacturer=m, deviceType=dt, customUser="u", customPass="p", area=a)

		req = self.factory.post(f"/api/networkdevice/{nd.id}/command/", {"command": "show ver"}, format='json')
		force_authenticate(req, user=self.admin)
		resp = executeCommand(req, nd.id)
		self.assertEqual(resp.status_code, 200)
		self.assertIn("result", resp.data)

	def test_bulk_save_classified_hosts(self):
		m = Manufacturer.objects.create(name="M2", get_running_config="r", get_vlan_info="v")
		dt = DeviceType.objects.create(name="DT2")
		c = Country.objects.create(name="C2")
		s = Site.objects.create(name="S2", country=c)
		a = Area.objects.create(name="A2", site=s)

		hosts = [
			{
				"hostname": "h1",
				"ipAddress": "10.0.0.11",
				"model": "m",
				"manufacturer": str(m.id),
				"deviceType": str(dt.id),
				"area": str(a.id),
				"vaultCredential": None,
				"customUser": "u1",
				"customPass": "p1",
			}
		]

		req = self.factory.post("/api/networkdevice/bulk/save/", {"hosts": hosts}, format='json')
		force_authenticate(req, user=self.operator)
		resp = bulk_save_classified_hosts(req)
		self.assertEqual(resp.status_code, 201)
		self.assertGreater(resp.data.get("created", 0), 0)

	@patch("core.views.get_hosts_from_csv")
	@patch("core.views.HostClassifier")
	def test_from_csv_bulk_view(self, mock_classifier, mock_get_hosts):
		# prepare rule set and file
		rs = ClassificationRuleSet.objects.create(name="rset", rules={})
		mock_get_hosts.return_value = [{"hostname": "hcsv", "ipAddress": "1.1.1.1", "manufacturer": "M", "deviceType": "DT", "area": None, "vaultCredential": None, "customUser": "u", "customPass": "p"}]
		mock_classifier.return_value.classify_all.return_value = mock_get_hosts.return_value

		csv_file = SimpleUploadedFile("hosts.csv", b"hostname,ipAddress\nhcsv,1.1.1.1", content_type="text/csv")
		req = self.factory.post("/api/networkdevice/bulk/from-csv/", {"ruleSetId": str(rs.id), "file": csv_file})
		force_authenticate(req, user=self.admin)
		resp = from_csv_bulk_view(req)
		self.assertEqual(resp.status_code, 200)
		self.assertIsInstance(resp.data, list)

	@patch("core.views.subprocess.run")
	@patch("core.views.ZabbixManager")
	def test_zabbix_connectivity_status(self, mock_zm_cls, mock_run):
		# mock ping output
		mock_proc = Mock()
		mock_proc.stdout = "64 bytes from 1.2.3.4: icmp_seq=1 ttl=64 time=0.123 ms"
		mock_run.return_value = mock_proc

		zm = Mock()
		zm.connect.return_value = True
		mock_zm_cls.return_value = zm

		req = self.factory.get("/api/zabbix/status/")
		force_authenticate(req, user=self.admin)
		resp = zabbix_connectivity_status(req)
		self.assertEqual(resp.status_code, 200)
		self.assertIn("activate", resp.data)
		self.assertTrue(resp.data.get("activate"))

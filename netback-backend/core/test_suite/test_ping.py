from unittest.mock import patch, Mock
import subprocess

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from utils.ping import ping_ip
from core.models import UserSystem
from core.views import ping_device


class PingUtilsTests(TestCase):
	def test_ping_ip_reachable_parses_stats(self):
		mock_proc = Mock()
		mock_proc.returncode = 0
		mock_proc.stdout = "2 packets transmitted, 2 received, 0% packet loss"
		mock_proc.stderr = ""

		with patch("subprocess.run", return_value=mock_proc):
			res = ping_ip("10.0.0.1")
			self.assertTrue(res.get("reachable"))
			self.assertIn("stats", res)
			self.assertEqual(res["stats"].get("transmitted"), 2)
			self.assertEqual(res["stats"].get("received"), 2)

	def test_ping_ip_unreachable_unknown_host(self):
		mock_proc = Mock()
		mock_proc.returncode = 2
		mock_proc.stdout = "ping: unknown host foobar"
		mock_proc.stderr = ""

		with patch("subprocess.run", return_value=mock_proc):
			res = ping_ip("10.0.0.254")
			self.assertFalse(res.get("reachable"))
			self.assertEqual(res.get("error"), "unknown_host")

	def test_ping_ip_timeout(self):
		with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="ping", timeout=5)):
			res = ping_ip("10.0.0.5")
			self.assertFalse(res.get("reachable"))
			self.assertEqual(res.get("error"), "timeout")

	def test_ping_ip_no_binary(self):
		with patch("subprocess.run", side_effect=FileNotFoundError()):
			res = ping_ip("10.0.0.6")
			self.assertFalse(res.get("reachable"))
			self.assertEqual(res.get("error"), "no_ping_binary")


class PingViewTests(TestCase):
	def setUp(self):
		# create a basic user to attach to the request
		self.user = UserSystem.objects.create_user(username="tuser", email="t@t.t", password="pwd")
		self.factory = APIRequestFactory()

	@patch("core.views.ping_ip")
	def test_ping_device_view_success(self, mock_ping):
		mock_ping.return_value = {"ip": "10.0.0.1", "reachable": True, "stats": {"transmitted": 2, "received": 2}}
		req = self.factory.post("/api/ping/", {"ip": "10.0.0.1"}, format="json")
		force_authenticate(req, user=self.user)
		resp = ping_device(req)
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(resp.data.get("status"), "success")
		self.assertTrue(resp.data.get("data")["reachable"])

	@patch("core.views.ping_ip")
	def test_ping_device_view_unreachable(self, mock_ping):
		mock_ping.return_value = {"ip": "10.0.0.2", "reachable": False, "error": "network_unreachable"}
		req = self.factory.post("/api/ping/", {"ip": "10.0.0.2"}, format="json")
		force_authenticate(req, user=self.user)
		resp = ping_device(req)
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(resp.data.get("status"), "error")
		self.assertFalse(resp.data.get("data")["reachable"]) 

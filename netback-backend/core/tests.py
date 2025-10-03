from django.test import SimpleTestCase, override_settings
from utils.env import get_fernet
from cryptography.fernet import Fernet
from django.test import TestCase
from .models import VaultCredential, Manufacturer, DeviceType, Area, NetworkDevice
from .serializers import NetworkDeviceSerializer


class CryptoHelperTests(SimpleTestCase):
	def test_get_fernet_none_when_key_missing(self):
		with override_settings(ENCRYPTION_KEY_VAULT=None):
			f = get_fernet()
			self.assertIsNone(f)

	def test_get_fernet_returns_fernet_with_valid_key(self):
		key = Fernet.generate_key().decode()
		with override_settings(ENCRYPTION_KEY_VAULT=key):
			f = get_fernet()
			self.assertIsNotNone(f)
			token = f.encrypt(b"hello")
			self.assertEqual(f.decrypt(token), b"hello")

	def test_vaultcredential_save_raises_without_key(self):
		from .models import VaultCredential
		vc = VaultCredential(nick="n1", username="u1", password="secret")
		with override_settings(ENCRYPTION_KEY_VAULT=None):
			with self.assertRaises(RuntimeError):
				vc.save()

	def test_networkdevice_requires_vault_or_both_custom(self):
		# Setup related objects
		m = Manufacturer.objects.create(name="M1", get_running_config="show run", get_vlan_info="show vlan")
		dt = DeviceType.objects.create(name="DT1")
		country_area = None
		# create area via country/site minimal chain
		from .models import Country, Site, Area
		c = Country.objects.create(name="C1")
		s = Site.objects.create(name="S1", country=c)
		a = Area.objects.create(name="A1", site=s)

		# Case 1: no vault, no custom -> should fail validation
		data = {
			"hostname": "host1",
			"ipAddress": "10.0.0.1",
			"model": "mod",
			"manufacturer": str(m.id),
			"deviceType": str(dt.id),
			"area": str(a.id),
		}
		serializer = NetworkDeviceSerializer(data=data)
		self.assertFalse(serializer.is_valid())

		# Case 2: with vault only -> should be valid
		vc = VaultCredential.objects.create(nick="v1", username="vuser", password="vpass")
		data2 = {**data, "vaultCredential": str(vc.id)}
		serializer2 = NetworkDeviceSerializer(data=data2)
		self.assertTrue(serializer2.is_valid(), serializer2.errors)

		# Case 3: customUser present but no customPass -> invalid
		data3 = {**data, "customUser": "u1"}
		serializer3 = NetworkDeviceSerializer(data=data3)
		self.assertFalse(serializer3.is_valid())

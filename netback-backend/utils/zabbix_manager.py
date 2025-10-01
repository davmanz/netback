import csv
from zabbix_utils import ZabbixAPI

class ZabbixManager:
    def __init__(self, url, token):

        self.url = url
        self.token = token
        self.zapi = None

    def connect(self):
        print("🔄 Connecting to the Zabbix API...")
        try:
            self.zapi = ZabbixAPI(url=self.url, token=self.token)
            version = self.zapi.apiinfo.version()
            print(f"✅ Connected to Zabbix API version {version}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Zabbix API: {e}")
            raise

    def get_host_groups(self, group_names=None):

        try:
            params = {"output": ["groupid", "name"]}
            if group_names:
                params["filter"] = {"name": group_names}

            return self.zapi.hostgroup.get(**params)
        except Exception as e:
            print(f"❌ Failed to get host groups: {e}")
            return []

    def get_raw_hosts(self, group_ids=None):

        print("🔍 Fetching raw host data from Zabbix...")
        try:
            params = {
                "output": ["hostid", "host", "name"],
                "selectInterfaces": ["interfaceid", "ip"],
                "selectGroups": ["name"],
                "selectTags": ["tag", "value"],
            }
            if group_ids:
                params["groupids"] = group_ids

            return self.zapi.host.get(**params)
        except Exception as e:
            print(f"❌ Failed to get raw hosts: {e}")
            return []

    def get_processed_hosts(self, group_ids=None, tag_name="marca"):
        hosts = self.get_raw_hosts(group_ids)
        processed = []

        for host in hosts:
            host_id = host["hostid"]
            hostname = host["host"]
            visible_name = host["name"]
            ip = host["interfaces"][0]["ip"] if host.get("interfaces") else "No IP"
            groups = {g["name"] for g in host.get("groups", [])}  # ← set sin duplicados
            tag_value = self._extract_tag_value(host.get("tags", []), tag_name)

            processed.append(
                {
                    "hostid": host_id,
                    "hostname": hostname,
                    "name": visible_name,
                    "ip": ip,
                    "groups": groups,
                    "tags": tag_value,
                }
            )

        return processed

    def _extract_tag_value(self, tags, tag_name):

        for tag in tags:
            if tag["tag"] == tag_name:
                return tag["value"]
        return None

    def export_hosts_to_csv(self, hosts, filename="zabbix_hosts_export.csv"):

        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(
                    ["hostid", "host", "name", "ip", "groups", "tag"]
                )  # Header
                writer.writerows(hosts)
            print(f"✅ Hosts exported successfully to '{filename}'")
        except Exception as e:
            print(f"❌ Failed to export CSV: {e}")

    def disconnect(self):
        # Solo desconectar si se usó login (no token)
        if self.zapi and not self.token:
            try:
                self.zapi.user.logout()
                print("🔌 Disconnected from Zabbix API")
            except Exception as e:
                print(f"⚠ No se pudo cerrar sesión: {str(e)}")
        else:
            print("ℹ️ No se requiere logout con token de autenticación")
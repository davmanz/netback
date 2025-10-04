from tools.smoke.common import ProxySession, random_nick


def main():
    s = ProxySession(timeout=30.0)
    rid = None
    vid = None
    try:
        print("Login...")
        s.login()

        # 1) GET /zabbix/status/ debe existir y devolver algún JSON (200 o error manejado)
        st = s.get("/zabbix/status/")
        print("zabbix status:", st.status_code, st.text[:120])
        assert st.status_code != 404
        # Debe ser parseable como JSON (mensaje de error o status)
        _ = st.json()

        # 2) POST /networkdevice/bulk/from-zabbix/ sin ruleSetId debe dar 400 (validación backend)
        no_id = s.post("/networkdevice/bulk/from-zabbix/", {})
        print("from-zabbix without ruleSetId:", no_id.status_code, no_id.text)
        assert no_id.status_code == 400

        # 3) Crear recursos mínimos para intentar con ruleSetId (independiente de Zabbix real)
        vnick = random_nick("vault")
        vc = s.post("/vaultcredentials/", {"nick": vnick, "username": "vuser", "password": "vpass"})
        assert vc.status_code in (200, 201)
        vid = vc.json()["id"]

        name = random_nick("ruleset")
        rules = {
            "country": ["Perú"],
            "site": ["Arequipa"],
            "area": ["Administracion"],
            "model": ["modelX"],
            "deviceType": ["Desconocido"],
            "manufacturer": ["Cisco"],
        }
        rs = s.post("/classification-rules/", {"name": name, "rules": rules, "vaultCredential": vid})
        assert rs.status_code in (200, 201)
        rid = rs.json()["id"]

        # 4) POST /networkdevice/bulk/from-zabbix/ con ruleSetId
        with_id = s.post("/networkdevice/bulk/from-zabbix/", {"ruleSetId": rid})
        print("from-zabbix with ruleSetId:", with_id.status_code, with_id.text[:200])
        # Aceptamos éxito o error según entorno, pero debe ser JSON válido y no 404
        assert with_id.status_code != 404
        _ = with_id.json()

        # Limpieza
        if rid:
            s.delete(f"/classification-rules/{rid}/")
        if vid:
            s.delete(f"/vaultcredentials/{vid}/")

        print("OK")
    finally:
        s.close()


if __name__ == "__main__":
    main()

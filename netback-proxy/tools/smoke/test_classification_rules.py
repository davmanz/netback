from tools.smoke.common import ProxySession, random_nick


def main():
    s = ProxySession()
    rid = None
    vid = None
    try:
        print("Login...")
        s.login()

        # Crear credencial de vault para asociar al ruleset
        vnick = random_nick("vault")
        vc = s.post("/vaultcredentials/", {"nick": vnick, "username": "vuser", "password": "vpass"})
        assert vc.status_code in (200, 201)
        vid = vc.json()["id"]

        # Crear ruleset
        name = random_nick("ruleset")
        rules = {
            "country": ["Perú"],
            "site": ["Arequipa"],
            "area": ["Administracion"],
            "model": ["modelX"],
            "deviceType": ["Desconocido"],
            "manufacturer": ["Cisco"],
        }
        create = s.post("/classification-rules/", {"name": name, "rules": rules, "vaultCredential": vid})
        print("create ruleset:", create.status_code, create.text)
        assert create.status_code in (200, 201)
        rid = create.json()["id"]

        # Listar
        lst = s.get("/classification-rules/")
        print("list rulesets:", lst.status_code)
        assert lst.status_code == 200

        # Update (PUT)
        rules_upd = dict(rules)
        rules_upd["model"] = ["modelY"]
        upd = s.put(f"/classification-rules/{rid}/", {"name": name + "-upd", "rules": rules_upd, "vaultCredential": vid})
        print("update ruleset:", upd.status_code, upd.text)
        assert upd.status_code in (200, 202)

        # Delete
        dele = s.delete(f"/classification-rules/{rid}/")
        print("delete ruleset:", dele.status_code, dele.text)
        assert dele.status_code in (200, 204)

        # Cleanup vault
        if vid:
            s.delete(f"/vaultcredentials/{vid}/")

        print("OK")
    finally:
        s.close()


if __name__ == "__main__":
    main()

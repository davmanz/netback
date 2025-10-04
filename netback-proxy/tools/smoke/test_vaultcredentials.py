from tools.smoke.common import ProxySession, random_nick


def main():
    s = ProxySession()
    try:
        print("Login...")
        s.login()

        print("Create vault credential...")
        nick = random_nick("vault")
        create = s.post("/vaultcredentials/", {"nick": nick, "username": "u1", "password": "p1"})
        print("create:", create.status_code, create.text)
        assert create.status_code in (200, 201)
        vid = create.json().get("id")
        assert vid

        print("List vault credentials...")
        lst = s.get("/vaultcredentials/")
        print("list:", lst.status_code)
        assert lst.status_code == 200

        print("Update vault credential...")
        upd = s.put(f"/vaultcredentials/{vid}/", {"nick": f"{nick}-upd", "username": "u2", "password": "p2"})
        print("update:", upd.status_code, upd.text)
        assert upd.status_code in (200, 202)

        print("Delete vault credential...")
        dele = s.delete(f"/vaultcredentials/{vid}/")
        print("delete:", dele.status_code, dele.text)
        assert dele.status_code in (200, 204)

        print("OK")
    finally:
        s.close()


if __name__ == "__main__":
    main()

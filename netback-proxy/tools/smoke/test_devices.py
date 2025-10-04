from tools.smoke.common import ProxySession, random_nick


def pick_id(lst, key="id"):
    for item in lst:
        if key in item:
            return item[key]
    return None


def main():
    s = ProxySession()
    try:
        print("Login...")
        s.login()

        # Obtener FK requeridas
        mans = s.get("/manufacturers/")
        dts = s.get("/devicetypes/")
        areas = s.get("/areas/")
        assert mans.status_code == 200 and dts.status_code == 200 and areas.status_code == 200
        mid = pick_id(mans.json())
        dtid = pick_id(dts.json())
        aid = pick_id(areas.json())
        assert mid and dtid and aid, "Se requieren manufacturer/deviceType/area existentes"

        # Crear credencial vault temporal para cumplir validación
        vnick = random_nick("vault")
        vc = s.post("/vaultcredentials/", {"nick": vnick, "username": "vuser", "password": "vpass"})
        assert vc.status_code in (200, 201)
        vid = vc.json()["id"]

        # Crear dispositivo
        hostname = random_nick("sw")
        create = s.post(
            "/networkdevice/",
            {
                "hostname": hostname,
                "ipAddress": "10.0.0.250",
                "model": "modelX",
                "manufacturer": mid,
                "deviceType": dtid,
                "area": aid,
                "vaultCredential": vid,
            },
        )
        print("create device:", create.status_code, create.text)
        assert create.status_code in (200, 201)
        did = create.json()["id"]

        # Obtener y actualizar
        get1 = s.get(f"/networkdevice/{did}/")
        print("get device:", get1.status_code)
        assert get1.status_code == 200

        upd = s.patch(f"/networkdevice/{did}/", {"model": "modelY"})
        print("update device:", upd.status_code, upd.text)
        assert upd.status_code in (200, 202)

        # Borrar dispositivo
        dele = s.delete(f"/networkdevice/{did}/")
        print("delete device:", dele.status_code, dele.text)
        assert dele.status_code in (200, 204)

        # Cleanup vault
        s.delete(f"/vaultcredentials/{vid}/")

        print("OK")
    finally:
        s.close()


if __name__ == "__main__":
    main()

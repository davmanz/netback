from tools.smoke.common import ProxySession, random_nick


def contains_id(items, target_id: str) -> bool:
    try:
        for it in items:
            if it.get("id") == target_id:
                return True
    except Exception:
        return False
    return False


def main():
    s = ProxySession()
    country_id = site_id = area_id = None
    try:
        print("Login...")
        s.login()

        # Crear Country
        cname = random_nick("country")
        c_resp = s.post("/countries/", {"name": cname})
        print("create country:", c_resp.status_code, c_resp.text)
        assert c_resp.status_code in (200, 201)
        country_id = c_resp.json()["id"]

        # Listar Countries y verificar
        c_list = s.get("/countries/")
        print("list countries:", c_list.status_code)
        assert c_list.status_code == 200
        assert contains_id(c_list.json(), country_id)

        # Crear Site ligado al Country
        sname = random_nick("site")
        s_resp = s.post("/sites/", {"name": sname, "country": country_id})
        print("create site:", s_resp.status_code, s_resp.text)
        assert s_resp.status_code in (200, 201)
        site_id = s_resp.json()["id"]

        # Listar Sites filtrando por country_id y verificar
        s_list = s.get(f"/sites/?country_id={country_id}")
        print("list sites:", s_list.status_code)
        assert s_list.status_code == 200
        assert contains_id(s_list.json(), site_id)

        # Crear Area ligada al Site
        aname = random_nick("area")
        a_resp = s.post("/areas/", {"name": aname, "site": site_id})
        print("create area:", a_resp.status_code, a_resp.text)
        assert a_resp.status_code in (200, 201)
        area_id = a_resp.json()["id"]

        # Listar Areas filtrando por site_id y verificar
        a_list = s.get(f"/areas/?site_id={site_id}")
        print("list areas:", a_list.status_code)
        assert a_list.status_code == 200
        assert contains_id(a_list.json(), area_id)

        # PATCH actualizaciones parciales
        pc = s.patch(f"/countries/{country_id}/", {"name": cname + "-upd"})
        print("patch country:", pc.status_code, pc.text)
        assert pc.status_code in (200, 202)

        ps = s.patch(f"/sites/{site_id}/", {"name": sname + "-upd"})
        print("patch site:", ps.status_code, ps.text)
        assert ps.status_code in (200, 202)

        pa = s.patch(f"/areas/{area_id}/", {"name": aname + "-upd"})
        print("patch area:", pa.status_code, pa.text)
        assert pa.status_code in (200, 202)

        # Limpieza usando proxy catch-all /api (DELETE no está mapeado en locations)
        if area_id:
            da = s.delete(f"/api/areas/{area_id}/")
            print("delete area:", da.status_code)
            assert da.status_code in (200, 204)
        if site_id:
            ds = s.delete(f"/api/sites/{site_id}/")
            print("delete site:", ds.status_code)
            assert ds.status_code in (200, 204)
        if country_id:
            dc = s.delete(f"/api/countries/{country_id}/")
            print("delete country:", dc.status_code)
            assert dc.status_code in (200, 204)

        print("OK")
    finally:
        s.close()


if __name__ == "__main__":
    main()

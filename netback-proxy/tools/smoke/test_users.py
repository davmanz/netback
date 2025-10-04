from tools.smoke.common import ProxySession, random_nick


def main():
    s = ProxySession()
    try:
        print("Login...")
        s.login()

        uname = random_nick("user")
        print("Create user (admin only)...")
        create = s.post(
            "/users/",
            {
                "username": uname,
                "email": f"{uname}@example.com",
                "password": "S3cret!123",
                "role": "viewer",
            },
        )
        print("create:", create.status_code, create.text)
        assert create.status_code in (200, 201)
        uid = create.json().get("id")
        assert uid

        print("List users (admin only)...")
        lst = s.get("/users/")
        print("list:", lst.status_code)
        assert lst.status_code == 200

        print("Update user (admin only)...")
        upd = s.patch(
            f"/users/{uid}/",
            {"email": f"{uname}+upd@example.com"},
        )
        print("update:", upd.status_code, upd.text)
        assert upd.status_code in (200, 202)

        print("Delete user (admin only)...")
        dele = s.delete(f"/users/{uid}/")
        print("delete:", dele.status_code, dele.text)
        assert dele.status_code in (200, 204)

        print("OK")
    finally:
        s.close()


if __name__ == "__main__":
    main()

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "List all VaultCredential entries and show encryption/decoding status (no passwords in clear)."

    def handle(self, *args, **options):
        try:
            from core.models import VaultCredential
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing VaultCredential: {e}"))
            return

        vaults = VaultCredential.objects.all()
        if not vaults:
            self.stdout.write("No VaultCredential entries found.")
            return

        self.stdout.write(f"Found {vaults.count()} VaultCredential(s):")
        for vc in vaults:
            stored = vc.password or ""
            looks_fernet = isinstance(stored, str) and stored.startswith("gAAAAA")
            decrypt_ok = False
            preview = "-"
            try:
                plain = vc.get_plain_password()
                if plain is not None:
                    decrypt_ok = True
                    # mask preview: show first 2 and last 2 chars, and length
                    if len(plain) <= 6:
                        preview = plain
                    else:
                        preview = f"{plain[:2]}***{plain[-2:]} (len={len(plain)})"
            except Exception as e:
                preview = f"decrypt_error: {e}"

            self.stdout.write("----------------------------------------")
            self.stdout.write(f"id: {vc.id}")
            self.stdout.write(f"nick: {vc.nick}")
            self.stdout.write(f"username: {vc.username}")
            self.stdout.write(f"stored_looks_fernet: {looks_fernet}")
            self.stdout.write(f"decrypt_ok: {decrypt_ok}")
            self.stdout.write(f"preview: {preview}")

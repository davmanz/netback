from django.core.management.base import BaseCommand
from django.conf import settings
from utils.env import get_fernet, get_encryption_cipher

try:
    # Import local model lazily para evitar errores si se ejecuta fuera del contexto Django
    from core.models import VaultCredential
except Exception:
    VaultCredential = None


class Command(BaseCommand):
    help = "Debug VaultCredential encryption/decryption"

    def add_arguments(self, parser):
        parser.add_argument("--id", type=str, help="UUID of VaultCredential to inspect")
        parser.add_argument("--password", type=str, help="Plain password to encrypt/decrypt test")
        parser.add_argument("--create", action="store_true", help="Create a VaultCredential with provided nick/username/password (requires DB)")
        parser.add_argument("--nick", type=str, default="debug-nick")
        parser.add_argument("--username", type=str, default="debug-user")

    def handle(self, *args, **options):
        self.stdout.write("--- Vault debug ---")

        key = getattr(settings, "ENCRYPTION_KEY_VAULT", None)
        self.stdout.write(f"ENCRYPTION_KEY_VAULT set: {bool(key)}")
        if key:
            self.stdout.write(f"Key (first 8 chars): {str(key)[:8]}... (len={len(str(key))})")

        f = get_fernet()
        self.stdout.write(f"get_fernet() -> {'OK' if f else 'None / invalid key'}")

        # probar cifrado/descifrado con una contraseña proporcionada
        pw = options.get("password")
        if pw:
            if not f:
                self.stdout.write(self.style.ERROR("No hay cifrador disponible para probar (get_fernet devolvió None)."))
            else:
                token = f.encrypt(pw.encode()).decode()
                self.stdout.write(f"Encrypted token: {token}")
                try:
                    dec = f.decrypt(token.encode()).decode()
                    self.stdout.write(f"Decrypted back: {dec}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Decrypt failed: {e}"))

        # inspeccionar objeto en BD si se pide
        vid = options.get("id")
        if vid:
            if VaultCredential is None:
                self.stdout.write(self.style.ERROR("Modelo VaultCredential no disponible (import falló)."))
                return
            try:
                vc = VaultCredential.objects.filter(id=vid).first()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error accediendo a la BD: {e}"))
                return
            if not vc:
                self.stdout.write(self.style.WARNING(f"No se encontró VaultCredential con id={vid}"))
                return

            self.stdout.write(f"Found VaultCredential: nick={vc.nick} username={vc.username}")
            raw = vc.password
            self.stdout.write(f"Stored (raw) value: {raw}")

            if not f:
                self.stdout.write(self.style.WARNING("get_fernet() devolvió None — intentando get_encryption_cipher() (esta función levanta si falta clave)."))
                try:
                    f2 = get_encryption_cipher()
                    self.stdout.write("get_encryption_cipher() -> OK")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"get_encryption_cipher() error: {e}"))
                    return
            else:
                f2 = f

            # Intentar descifrar raw con f2
            try:
                if isinstance(raw, str) and raw.startswith("gAAAAA"):
                    dec = f2.decrypt(raw.encode()).decode()
                    self.stdout.write(self.style.SUCCESS(f"Decrypted password: {dec}"))
                else:
                    self.stdout.write(self.style.WARNING("El valor almacenado no parece un token Fernet (no empieza por 'gAAAAA')."))
                    # intentar decrypt de todas formas
                    try:
                        dec = f2.decrypt(raw.encode()).decode()
                        self.stdout.write(self.style.SUCCESS(f"Decrypted anyway: {dec}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Decrypt raised: {e}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al descifrar: {e}"))

        # Crear un VC de prueba (opcional)
        if options.get("create"):
            if VaultCredential is None:
                self.stdout.write(self.style.ERROR("Modelo VaultCredential no disponible (import falló)."))
                return
            if not options.get("password"):
                self.stdout.write(self.style.ERROR("--password es requerido para --create"))
                return
            try:
                vc2 = VaultCredential.objects.create(nick=options.get("nick"), username=options.get("username"), password=options.get("password"))
                self.stdout.write(self.style.SUCCESS(f"Created VaultCredential id={vc2.id} stored={vc2.password}"))
                # mostrar descifrado
                try:
                    self.stdout.write(f"get_plain_password() -> {vc2.get_plain_password()}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"get_plain_password() error: {e}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creando VaultCredential: {e}"))

        self.stdout.write("--- done ---")

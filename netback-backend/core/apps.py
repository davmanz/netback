from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Core"

    def ready(self):
        # Import signals to ensure they are registered when the app is ready
        try:
            import core.signals  # noqa: F401
        except Exception:
            # Avoid crashing if signals cannot be imported during certain management commands
            pass

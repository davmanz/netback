from django.conf import settings
from django.http import JsonResponse


class CSRFDobleSubmitMiddleware:
    """Middleware simple para validar X-CSRF-Token contra la cookie XSRF-TOKEN.

    - Solo valida para métodos mutantes: POST, PUT, PATCH, DELETE
    - Excluye rutas configuradas en settings.CSRF_EXEMPT_PATHS
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_paths = getattr(settings, "CSRF_EXEMPT_PATHS", [
            "/api/token/",
            "/api/token/refresh/",
            "/api/token/logout/",
            "/api/health/",
        ])

    def __call__(self, request):
        method = request.method.upper()
        if method in ("POST", "PUT", "PATCH", "DELETE"):
            path = request.path
            if not any(path.startswith(p) for p in self.exempt_paths):
                cookie_val = request.COOKIES.get(getattr(settings, "CSRF_COOKIE_NAME", "XSRF-TOKEN"))
                header_val = request.META.get("HTTP_X_CSRF_TOKEN")
                if not cookie_val or not header_val or cookie_val != header_val:
                    return JsonResponse({"detail": "CSRF token inválido"}, status=403)

        return self.get_response(request)

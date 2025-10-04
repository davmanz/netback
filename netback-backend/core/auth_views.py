from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import uuid
from rest_framework import status


class CookieTokenObtainPairView(TokenObtainPairView):
    """Extiende TokenObtainPairView para establecer el refresh token como cookie httpOnly.
    Devuelve el access token en el body y guarda el refresh en cookie segura.
    """
    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        # Si la autenticación fue exitosa, el serializer incluirá 'refresh'
        refresh = resp.data.get("refresh")
        if refresh:
            # Establecer cookie httpOnly para refresh
            resp.set_cookie(
                key=getattr(settings, "JWT_REFRESH_COOKIE_NAME", "refresh"),
                value=refresh,
                httponly=True,
                secure=getattr(settings, "JWT_REFRESH_COOKIE_SECURE", False),
                samesite=getattr(settings, "JWT_REFRESH_COOKIE_SAMESITE", "Lax"),
                path=getattr(settings, "JWT_REFRESH_COOKIE_PATH", "/"),
                max_age=getattr(settings, "JWT_REFRESH_COOKIE_MAX_AGE", 604800),
            )
            # Emitir también un token CSRF accesible desde JS (double-submit cookie)
            xsrf = str(uuid.uuid4())
            resp.set_cookie(
                key=getattr(settings, "CSRF_COOKIE_NAME", "XSRF-TOKEN"),
                value=xsrf,
                httponly=False,
                secure=getattr(settings, "CSRF_COOKIE_SECURE", False),
                samesite=getattr(settings, "CSRF_COOKIE_SAMESITE", "Lax"),
                path="/",
                max_age=getattr(settings, "JWT_REFRESH_COOKIE_MAX_AGE", 604800),
            )
            # Remover refresh del body por seguridad
            resp.data.pop("refresh", None)
        return resp


class CookieTokenRefreshView(TokenRefreshView):
    """Lee el refresh token desde la cookie si no se proporciona en el body.
    Devuelve un nuevo access (y rota el refresh si está configurado),
    almacenando el nuevo refresh en cookie si se emite.
    """
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        if "refresh" not in data:
            cookie = request.COOKIES.get(getattr(settings, "JWT_REFRESH_COOKIE_NAME", "refresh"))
            if cookie:
                data["refresh"] = cookie

        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"detail": "Refresh token inválido"}, status=status.HTTP_401_UNAUTHORIZED)

        response_data = serializer.validated_data
        resp = Response(response_data)

        # Si el proceso devolvió un nuevo refresh (rotación), lo guardamos en cookie
        new_refresh = response_data.get("refresh")
        if new_refresh:
            resp.set_cookie(
                key=getattr(settings, "JWT_REFRESH_COOKIE_NAME", "refresh"),
                value=new_refresh,
                httponly=True,
                secure=getattr(settings, "JWT_REFRESH_COOKIE_SECURE", False),
                samesite=getattr(settings, "JWT_REFRESH_COOKIE_SAMESITE", "Lax"),
                path=getattr(settings, "JWT_REFRESH_COOKIE_PATH", "/"),
                max_age=getattr(settings, "JWT_REFRESH_COOKIE_MAX_AGE", 604800),
            )
            # Remover refresh del body por seguridad
            resp.data.pop("refresh", None)
            # Rotate XSRF token together with refresh rotation
            xsrf = str(uuid.uuid4())
            resp.set_cookie(
                key=getattr(settings, "CSRF_COOKIE_NAME", "XSRF-TOKEN"),
                value=xsrf,
                httponly=False,
                secure=getattr(settings, "CSRF_COOKIE_SECURE", False),
                samesite=getattr(settings, "CSRF_COOKIE_SAMESITE", "Lax"),
                path="/",
                max_age=getattr(settings, "JWT_REFRESH_COOKIE_MAX_AGE", 604800),
            )

        return resp


@api_view(["POST"])
@permission_classes([AllowAny])
def logout_view(request):
    """Eliminar cookie de refresh en logout.
    También podría invalidar refresh tokens en backend si se implementa blacklisting.
    """
    resp = Response({"detail": "logged out"}, status=status.HTTP_200_OK)
    resp.delete_cookie(getattr(settings, "JWT_REFRESH_COOKIE_NAME", "refresh"), path=getattr(settings, "JWT_REFRESH_COOKIE_PATH", "/"))
    # borrar cookie XSRF también
    resp.delete_cookie(getattr(settings, "CSRF_COOKIE_NAME", "XSRF-TOKEN"), path="/")
    return resp

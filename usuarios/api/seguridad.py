"""Seguridad de la API: token firmado que identifica al cuidador.

Flujo: el cuidador hace login -> recibe un token -> lo manda en cada petición
en la cabecera  Authorization: Bearer <token>.
"""
from functools import wraps

from django.core import signing
from django.http import JsonResponse

SAL = "cuidartech-api"
VIDA_TOKEN_SEGUNDOS = 60 * 60 * 8  # el token dura 8 horas
ROL_CUIDADOR = 1


def crear_token(usuario):
    """Genera un token firmado con el id y el rol del usuario."""
    return signing.dumps(
        {"id": usuario.id_usuario, "rol": usuario.id_rol}, salt=SAL
    )


def requiere_token(vista):
    """Decorador: deja pasar solo peticiones con un token válido de cuidador."""

    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        cabecera = request.headers.get("Authorization", "")
        if not cabecera.startswith("Bearer "):
            return JsonResponse(
                {"error": "Falta el token. Usa la cabecera Authorization: Bearer <token>."},
                status=401,
            )
        try:
            datos = signing.loads(
                cabecera[len("Bearer "):], salt=SAL, max_age=VIDA_TOKEN_SEGUNDOS
            )
        except signing.SignatureExpired:
            return JsonResponse({"error": "El token expiró. Vuelve a iniciar sesión."}, status=401)
        except signing.BadSignature:
            return JsonResponse({"error": "Token inválido."}, status=401)

        if datos.get("rol") != ROL_CUIDADOR:
            return JsonResponse(
                {"error": "Solo los cuidadores pueden usar este recurso."}, status=403
            )

        request.id_cuidador = datos["id"]  # la vista sabe quién llama
        return vista(request, *args, **kwargs)

    return envoltura
"""API REST del módulo Gestión de Pacientes.

Estas vistas SOLO traducen HTTP <-> fachada: leen la petición, llaman a
PacienteFacade (donde vive la lógica de negocio) y devuelven JSON con el
código de estado correcto. No validan reglas de negocio aquí.
"""
import json

from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..repositories.usuario_repository import UsuarioRepository
from ..services.pacientes.builder import PacienteInvalidoError
from ..services.pacientes.facade import PacienteFacade
from .seguridad import VIDA_TOKEN_SEGUNDOS, crear_token, requiere_token

facade = PacienteFacade()

CAMPOS_TEXTO = (
    "nombre", "apellidos", "tipo_documento", "numero_documento",
    "fecha_nacimiento", "sexo", "contacto_emergencia", "diagnostico",
)


# ── Funciones de apoyo ─────────────────────────────────────────────────────────
def _error(estado, mensaje):
    return JsonResponse({"error": mensaje}, status=estado)


def _paciente_a_dict(p):
    return {
        "id_paciente": p.id_paciente,
        "nombre": p.nombre,
        "apellidos": p.apellidos,
        "tipo_documento": p.tipo_documento,
        "numero_documento": p.numero_documento,
        "fecha_nacimiento": p.fecha_nacimiento.isoformat(),
        "sexo": p.sexo,
        "contacto_emergencia": p.contacto_emergencia,
        "diagnostico": p.diagnostico,
        "estado": p.estado,
    }


def _leer_json(request):
    """Devuelve (datos, None) si el cuerpo es válido, o (None, respuesta_de_error)."""
    try:
        datos = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None, _error(400, "El cuerpo de la petición debe ser un JSON válido.")
    if not isinstance(datos, dict):
        return None, _error(400, "El cuerpo debe ser un objeto JSON.")
    no_texto = [
        c for c in CAMPOS_TEXTO
        if datos.get(c) is not None and not isinstance(datos[c], str)
    ]
    if no_texto:
        return None, _error(400, "Estos campos deben ser texto: " + ", ".join(no_texto) + ".")
    return datos, None


def _respuesta_invalido(error):
    """409 si el documento ya existe; 400 para cualquier otro dato inválido."""
    duplicado = any("Ya existe" in e for e in error.errores)
    return JsonResponse({"errores": error.errores}, status=409 if duplicado else 400)


# ── Endpoints ──────────────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    """POST /api/auth/login/ -> entrega el token."""
    datos, error = _leer_json(request)
    if error:
        return error
    usuario = UsuarioRepository().buscar_por_correo(datos.get("correo"))
    clave = str(datos.get("password") or "")
    if usuario is None or not check_password(clave, usuario.password):
        return _error(401, "Correo o contraseña incorrectos.")
    return JsonResponse({
        "token": crear_token(usuario),
        "tipo": "Bearer",
        "expira_en_segundos": VIDA_TOKEN_SEGUNDOS,
    })


@csrf_exempt
@require_http_methods(["GET", "POST"])
@requiere_token
def pacientes(request):
    """GET /api/pacientes/  -> lista los pacientes del cuidador.
    POST /api/pacientes/ -> registra un paciente (201)."""
    if request.method == "GET":
        lista = [_paciente_a_dict(p) for p in facade.listar(request.id_cuidador)]
        return JsonResponse({"total": len(lista), "pacientes": lista})

    datos, error = _leer_json(request)
    if error:
        return error
    try:
        paciente = facade.registrar(datos, request.id_cuidador)
    except PacienteInvalidoError as e:
        return _respuesta_invalido(e)
    return JsonResponse(_paciente_a_dict(paciente), status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
@requiere_token
def paciente_detalle(request, id_paciente):
    """GET    /api/pacientes/<id>/ -> consulta un paciente.
    PUT    /api/pacientes/<id>/ -> actualiza todos sus datos.
    DELETE /api/pacientes/<id>/ -> lo desactiva (eliminación lógica)."""
    if request.method == "GET":
        paciente = facade.consultar(id_paciente, request.id_cuidador)
    else:
        paciente = facade.obtener(id_paciente, request.id_cuidador)
    if paciente is None:
        return _error(404, "No existe un paciente con ese id para este cuidador.")

    if request.method == "GET":
        return JsonResponse(_paciente_a_dict(paciente))

    if request.method == "PUT":
        datos, error = _leer_json(request)
        if error:
            return error
        try:
            paciente = facade.actualizar(paciente, datos, request.id_cuidador)
        except PacienteInvalidoError as e:
            return _respuesta_invalido(e)
        return JsonResponse(_paciente_a_dict(paciente))

    paciente = facade.desactivar(paciente, request.id_cuidador)  # DELETE
    return JsonResponse({
        "mensaje": "Paciente desactivado. Su historial se conserva.",
        "paciente": _paciente_a_dict(paciente),
    })


@csrf_exempt
@require_http_methods(["GET"])
@requiere_token
def auditoria(request):
    """GET /api/pacientes/auditoria/ -> historial de acciones sobre los pacientes."""
    registros = [
        {
            "id_auditoria": r.id_auditoria,
            "id_paciente": r.id_paciente_id,
            "id_usuario": r.id_usuario_id,
            "accion": r.accion,
            "detalle": r.detalle,
            "fecha": r.fecha.isoformat(),
        }
        for r in facade.historial_auditoria(request.id_cuidador)
    ]
    return JsonResponse({"total": len(registros), "registros": registros})
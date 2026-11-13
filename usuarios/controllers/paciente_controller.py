from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, redirect

from usuarios.controllers.decorators import solo_cuidador
from usuarios.pacientes.builder import PacienteInvalidoError
from usuarios.pacientes.facade import PacienteFacade
from usuarios.services.exceptions import (
    PacienteNoEncontradoError,
    FamiliarNoEncontradoError,
    FamiliarYaAsignadoError,
)
from usuarios.services.pacientes.service import PacienteService

pacientes_facade = PacienteFacade()
paciente_service = PacienteService()


def _paciente_del_cuidador(id_paciente, usuario_id):
    try:
        return paciente_service.obtener_de_cuidador(id_paciente, usuario_id)
    except PacienteNoEncontradoError:
        raise Http404("Paciente no encontrado")


# ── LISTA PACIENTES ────────────────────────────────────────────────────────────
@solo_cuidador
def lista_pacientes(request):
    pacientes = pacientes_facade.listar(request.session.get('usuario_id'))
    return render(request, 'pacientes/lista_pacientes.html', {'pacientes': pacientes})


# ── AGREGAR PACIENTE ───────────────────────────────────────────────────────────
@solo_cuidador
def agregar_paciente(request):
    if request.method == 'POST':
        try:
            pacientes_facade.registrar(request.POST, request.session.get('usuario_id'))
        except PacienteInvalidoError as e:
            return render(request, 'pacientes/agregar_paciente.html',
                          {'errores': e.errores, 'datos': request.POST})
        messages.success(request, 'Paciente registrado correctamente.')
        return redirect('lista_pacientes')
    return render(request, 'pacientes/agregar_paciente.html')


# ── DETALLE PACIENTE ───────────────────────────────────────────────────────────
@solo_cuidador
def detalle_paciente(request, id_paciente):
    paciente = pacientes_facade.consultar(id_paciente, request.session.get('usuario_id'))
    if paciente is None:
        return redirect('lista_pacientes')
    return render(request, 'pacientes/detalle_paciente.html', {'paciente': paciente})


# ── EDITAR PACIENTE ────────────────────────────────────────────────────────────
@solo_cuidador
def editar_paciente(request, id_paciente):
    usuario_id = request.session.get('usuario_id')
    paciente = pacientes_facade.obtener(id_paciente, usuario_id)
    if paciente is None:
        return redirect('lista_pacientes')

    if request.method == 'POST':
        try:
            pacientes_facade.actualizar(paciente, request.POST, usuario_id)
        except PacienteInvalidoError as e:
            return render(request, 'pacientes/editar_paciente.html',
                          {'paciente': paciente, 'errores': e.errores, 'datos': request.POST})
        messages.success(request, 'Paciente actualizado correctamente.')
        return redirect('lista_pacientes')

    return render(request, 'pacientes/editar_paciente.html', {
        'paciente': paciente,
        'datos': pacientes_facade.datos_formulario(paciente),
    })


# ── DESACTIVAR PACIENTE ────────────────────────────────────────────────────────
@solo_cuidador
def desactivar_paciente(request, id_paciente):
    usuario_id = request.session.get('usuario_id')
    paciente = pacientes_facade.obtener(id_paciente, usuario_id)
    if paciente:
        pacientes_facade.desactivar(paciente, usuario_id)
        messages.success(request, f'Paciente {paciente.nombre} desactivado.')
    return redirect('lista_pacientes')


# ── AUDITORÍA DE PACIENTES ─────────────────────────────────────────────────────
@solo_cuidador
def auditoria_pacientes(request):
    registros = pacientes_facade.historial_auditoria(request.session.get('usuario_id'))
    return render(request, 'pacientes/auditoria.html', {'registros': registros})


# ── GESTIONAR FAMILIARES ───────────────────────────────────────────────────────
@solo_cuidador
def gestionar_familiares(request, id_paciente):
    usuario_id = request.session.get('usuario_id')
    paciente = _paciente_del_cuidador(id_paciente, usuario_id)
    error = None

    if request.method == 'POST':
        correo = request.POST.get('correo', '').strip()
        try:
            familiar = paciente_service.asignar_familiar(paciente, correo)
            messages.success(request, f'{familiar.nombre} asignado correctamente.')
            return redirect('gestionar_familiares', id_paciente=id_paciente)
        except (FamiliarNoEncontradoError, FamiliarYaAsignadoError) as e:
            error = str(e)

    return render(request, 'pacientes/gestionar_familiares.html', {
        'paciente': paciente,
        'familiares_asignados': paciente_service.listar_familiares(paciente),
        'error': error,
    })


# ── QUITAR FAMILIAR ────────────────────────────────────────────────────────────
@solo_cuidador
def quitar_familiar(request, id_paciente, id_familiar):
    usuario_id = request.session.get('usuario_id')
    paciente = _paciente_del_cuidador(id_paciente, usuario_id)
    if paciente_service.quitar_familiar(paciente, id_familiar):
        messages.success(request, 'Familiar removido correctamente.')
    return redirect('gestionar_familiares', id_paciente=id_paciente)
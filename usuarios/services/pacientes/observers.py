"""
PATRÓN OBSERVER: cuando a un paciente le pasa algo (creado, actualizado,
consultado, desactivado), se avisa a todos los observadores suscritos.

Los observadores ya no usan el ORM: guardan a través de los repositorios.
"""
from abc import ABC, abstractmethod

from usuarios.repositories.paciente_repository import (
    AuditoriaPacienteRepository,
    NotificacionRepository,
)


class ObservadorPaciente(ABC):

    @abstractmethod
    def actualizar(self, evento, paciente, usuario_id):
        """Se ejecuta cada vez que el sujeto publica un evento."""


class AuditoriaObserver(ObservadorPaciente):

    def __init__(self, repositorio=None):
        self._repo = repositorio or AuditoriaPacienteRepository()

    def actualizar(self, evento, paciente, usuario_id):
        self._repo.registrar(
            usuario_id=usuario_id,
            paciente=paciente,
            accion=evento,
            detalle=f"{paciente.nombre} {paciente.apellidos}".strip(),
        )


class NotificacionFamiliaresObserver(ObservadorPaciente):

    MENSAJES = {
        "actualizado": "Se actualizaron los datos del paciente {nombre}.",
        "desactivado": "El paciente {nombre} fue desactivado.",
    }

    def __init__(self, repositorio=None):
        self._repo = repositorio or NotificacionRepository()

    def actualizar(self, evento, paciente, usuario_id):
        plantilla = self.MENSAJES.get(evento)
        if plantilla is None:
            return

        mensaje = plantilla.format(nombre=f"{paciente.nombre} {paciente.apellidos}".strip())
        for familiar in self._repo.familiares_de(paciente):
            self._repo.crear(familiar, mensaje)


class PacienteEventos:

    def __init__(self):
        self._observadores = []

    def suscribir(self, observador):
        self._observadores.append(observador)

    def desuscribir(self, observador):
        self._observadores.remove(observador)

    def notificar(self, evento, paciente, usuario_id):
        for observador in self._observadores:
            observador.actualizar(evento, paciente, usuario_id)
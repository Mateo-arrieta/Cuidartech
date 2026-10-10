from abc import ABC, abstractmethod

from ..models import AuditoriaPaciente, FamiliarPaciente, Notificacion


class ObservadorPaciente(ABC):
    
    @abstractmethod
    def actualizar(self, evento, paciente, usuario_id):
        """Se ejecuta cada vez que el sujeto publica un evento."""


class AuditoriaObserver(ObservadorPaciente):
    
    def actualizar(self, evento, paciente, usuario_id):
        AuditoriaPaciente.objects.create(
            id_usuario_id=usuario_id,
            id_paciente=paciente,
            accion=evento,
            detalle=f"{paciente.nombre} {paciente.apellidos}".strip(),
        )


class NotificacionFamiliaresObserver(ObservadorPaciente):
    
    MENSAJES = {
        "actualizado": "Se actualizaron los datos del paciente {nombre}.",
        "desactivado": "El paciente {nombre} fue desactivado.",
    }

    def actualizar(self, evento, paciente, usuario_id):
        plantilla = self.MENSAJES.get(evento)
        if plantilla is None:
            return

        mensaje = plantilla.format(nombre=f"{paciente.nombre} {paciente.apellidos}".strip())
        relaciones = FamiliarPaciente.objects.filter(
            id_paciente=paciente
        ).select_related("id_familiar")

        for relacion in relaciones:
            Notificacion.objects.create(
                id_usuario=relacion.id_familiar,
                mensaje=mensaje,
                estado="no_leida",
            )


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
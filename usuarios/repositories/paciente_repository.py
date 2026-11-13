"""
REPOSITORIO DE PACIENTES (capa de datos del MVC)

Aquí, y solo aquí, se habla con la base de datos usando el ORM de Django.
Los servicios (facade, builder, observers) le piden los datos a este archivo
en vez de usar "Paciente.objects..." directamente.
"""
from usuarios.models import (
    AuditoriaPaciente,
    FamiliarPaciente,
    Notificacion,
    Paciente,
    Usuario,
)

ROL_FAMILIAR = 2


class PacienteRepository:
    """Consultas y cambios sobre la tabla 'pacientes'."""

    def listar_por_cuidador(self, id_cuidador):
        return Paciente.objects.filter(id_cuidador_id=id_cuidador)

    def obtener_de_cuidador(self, id_paciente, id_cuidador):
        return Paciente.objects.filter(
            id_paciente=id_paciente,
            id_cuidador_id=id_cuidador,
        ).first()

    def guardar(self, paciente):
        paciente.save()
        return paciente

    def existe_documento(self, tipo_documento, numero_documento, excluir_id=None):
        repetidos = Paciente.objects.filter(
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
        )
        if excluir_id:
            repetidos = repetidos.exclude(id_paciente=excluir_id)
        return repetidos.exists()

    # ── Familiares asignados al paciente ─────────────────────────────────
    def listar_familiares(self, paciente):
        return FamiliarPaciente.objects.filter(
            id_paciente=paciente
        ).select_related("id_familiar")

    def buscar_familiar_por_correo(self, correo):
        return Usuario.objects.filter(correo=correo, id_rol=ROL_FAMILIAR).first()

    def familiar_esta_asignado(self, familiar, paciente):
        return FamiliarPaciente.objects.filter(
            id_familiar=familiar, id_paciente=paciente
        ).exists()

    def asignar_familiar(self, familiar, paciente):
        return FamiliarPaciente.objects.create(id_familiar=familiar, id_paciente=paciente)

    def quitar_familiar(self, paciente, id_familiar):
        """Devuelve True si había una relación y se borró."""
        borrados, _ = FamiliarPaciente.objects.filter(
            id_paciente=paciente, id_familiar_id=id_familiar
        ).delete()
        return borrados > 0


class AuditoriaPacienteRepository:
    """Consultas y cambios sobre la tabla de auditoría de pacientes."""

    def registrar(self, usuario_id, paciente, accion, detalle):
        return AuditoriaPaciente.objects.create(
            id_usuario_id=usuario_id,
            id_paciente=paciente,
            accion=accion,
            detalle=detalle,
        )

    def listar_por_cuidador(self, id_cuidador):
        return AuditoriaPaciente.objects.filter(
            id_paciente__id_cuidador_id=id_cuidador
        ).select_related("id_usuario", "id_paciente")


class NotificacionRepository:
    """Familiares de un paciente y notificaciones que se les envían."""

    def familiares_de(self, paciente):
        relaciones = FamiliarPaciente.objects.filter(
            id_paciente=paciente
        ).select_related("id_familiar")
        return [relacion.id_familiar for relacion in relaciones]

    def crear(self, usuario, mensaje):
        return Notificacion.objects.create(
            id_usuario=usuario,
            mensaje=mensaje,
            estado="no_leida",
        )
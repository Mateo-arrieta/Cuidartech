from ..models import AuditoriaPaciente, Paciente
from .builder import PacienteBuilder
from .observers import (
    AuditoriaObserver,
    NotificacionFamiliaresObserver,
    PacienteEventos,
)


class PacienteFacade:
   
    def __init__(self):
        self._eventos = PacienteEventos()
        self._eventos.suscribir(AuditoriaObserver())
        self._eventos.suscribir(NotificacionFamiliaresObserver())

    def listar(self, id_cuidador):
        return Paciente.objects.filter(id_cuidador_id=id_cuidador)

    def obtener(self, id_paciente, id_cuidador):
        
        return Paciente.objects.filter(
            id_paciente=id_paciente,
            id_cuidador_id=id_cuidador,
        ).first()

    def consultar(self, id_paciente, id_cuidador):
       
        paciente = self.obtener(id_paciente, id_cuidador)
        if paciente:
            self._eventos.notificar("consultado", paciente, id_cuidador)
        return paciente

    def registrar(self, datos, id_cuidador):
        paciente = self._preparar(PacienteBuilder(), datos, id_cuidador).build()
        paciente.save()
        self._eventos.notificar("creado", paciente, id_cuidador)
        return paciente

    def actualizar(self, paciente, datos, id_cuidador):
        paciente = self._preparar(PacienteBuilder(), datos, id_cuidador).build(paciente)
        paciente.save()
        self._eventos.notificar("actualizado", paciente, id_cuidador)
        return paciente

    def desactivar(self, paciente, id_usuario):
        paciente.estado = False
        paciente.save()
        self._eventos.notificar("desactivado", paciente, id_usuario)
        return paciente

    def historial_auditoria(self, id_cuidador):
        """Reporte de auditoría de los pacientes del cuidador (RNF-05)."""
        return AuditoriaPaciente.objects.filter(
            id_paciente__id_cuidador_id=id_cuidador
        ).select_related("id_usuario", "id_paciente")

    @staticmethod
    def datos_formulario(paciente):
        
        return {
            "nombre": paciente.nombre,
            "apellidos": paciente.apellidos,
            "tipo_documento": paciente.tipo_documento or "",
            "numero_documento": paciente.numero_documento or "",
            "fecha_nacimiento": paciente.fecha_nacimiento.isoformat(),
            "sexo": paciente.sexo or "",
            "contacto_emergencia": paciente.contacto_emergencia or "",
            "diagnostico": paciente.diagnostico or "",
        }

    @staticmethod
    def _preparar(builder, datos, id_cuidador):
        return (
            builder
            .con_datos_personales(
                datos.get("nombre"), datos.get("apellidos"),
                datos.get("fecha_nacimiento"), datos.get("sexo"))
            .con_documento(datos.get("tipo_documento"), datos.get("numero_documento"))
            .con_contacto_emergencia(datos.get("contacto_emergencia"))
            .con_diagnostico(datos.get("diagnostico"))
            .con_cuidador(id_cuidador)
        )
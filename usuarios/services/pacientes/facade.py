"""
PATRÓN FACADE: punto de entrada único del módulo Gestión de Pacientes.

Los controladores solo llaman a esta clase. Ella coordina:
  - el Builder (arma y valida el paciente),
  - el Repositorio (guarda y consulta en la base de datos),
  - los Observers (auditoría y notificaciones a familiares).
"""
from usuarios.repositories.paciente_repository import (
    AuditoriaPacienteRepository,
    PacienteRepository,
)

from .builder import PacienteBuilder
from .observers import (
    AuditoriaObserver,
    NotificacionFamiliaresObserver,
    PacienteEventos,
)


class PacienteFacade:

    def __init__(self, repositorio=None, repositorio_auditoria=None):
        self._repo = repositorio or PacienteRepository()
        self._repo_auditoria = repositorio_auditoria or AuditoriaPacienteRepository()

        self._eventos = PacienteEventos()
        self._eventos.suscribir(AuditoriaObserver())
        self._eventos.suscribir(NotificacionFamiliaresObserver())

    def listar(self, id_cuidador):
        return self._repo.listar_por_cuidador(id_cuidador)

    def obtener(self, id_paciente, id_cuidador):
        return self._repo.obtener_de_cuidador(id_paciente, id_cuidador)

    def consultar(self, id_paciente, id_cuidador):
        paciente = self.obtener(id_paciente, id_cuidador)
        if paciente:
            self._eventos.notificar("consultado", paciente, id_cuidador)
        return paciente

    def registrar(self, datos, id_cuidador):
        paciente = self._preparar(datos, id_cuidador).build()
        self._repo.guardar(paciente)
        self._eventos.notificar("creado", paciente, id_cuidador)
        return paciente

    def actualizar(self, paciente, datos, id_cuidador):
        paciente = self._preparar(datos, id_cuidador).build(paciente)
        self._repo.guardar(paciente)
        self._eventos.notificar("actualizado", paciente, id_cuidador)
        return paciente

    def desactivar(self, paciente, id_usuario):
        paciente.estado = False
        self._repo.guardar(paciente)
        self._eventos.notificar("desactivado", paciente, id_usuario)
        return paciente

    def historial_auditoria(self, id_cuidador):
        """Reporte de auditoría de los pacientes del cuidador (RNF-05)."""
        return self._repo_auditoria.listar_por_cuidador(id_cuidador)

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

    def _preparar(self, datos, id_cuidador):
        return (
            PacienteBuilder(self._repo)
            .con_datos_personales(
                datos.get("nombre"), datos.get("apellidos"),
                datos.get("fecha_nacimiento"), datos.get("sexo"))
            .con_documento(datos.get("tipo_documento"), datos.get("numero_documento"))
            .con_contacto_emergencia(datos.get("contacto_emergencia"))
            .con_diagnostico(datos.get("diagnostico"))
            .con_cuidador(id_cuidador)
        )
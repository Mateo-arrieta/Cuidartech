from usuarios.repositories.paciente_repository import PacienteRepository
from usuarios.services.exceptions import (
    PacienteNoEncontradoError,
    FamiliarNoEncontradoError,
    FamiliarYaAsignadoError,
)


class PacienteService:
    """Reglas de negocio del módulo Pacientes. No conoce HTTP ni templates."""

    def __init__(self, repo=None):
        self.repo = repo or PacienteRepository()  # inversión de dependencias

    def obtener_de_cuidador(self, id_paciente, id_cuidador):
        paciente = self.repo.obtener_de_cuidador(id_paciente, id_cuidador)
        if paciente is None:
            raise PacienteNoEncontradoError("Paciente no encontrado")
        return paciente

    def listar_familiares(self, paciente):
        return self.repo.listar_familiares(paciente)

    def asignar_familiar(self, paciente, correo):
        familiar = self.repo.buscar_familiar_por_correo(correo)
        if familiar is None:
            raise FamiliarNoEncontradoError(
                'No se encontró ningún familiar registrado con ese correo.')
        if self.repo.familiar_esta_asignado(familiar, paciente):
            raise FamiliarYaAsignadoError(
                'Este familiar ya está asignado a este paciente.')
        self.repo.asignar_familiar(familiar, paciente)
        return familiar

    def quitar_familiar(self, paciente, id_familiar):
        return self.repo.quitar_familiar(paciente, id_familiar)
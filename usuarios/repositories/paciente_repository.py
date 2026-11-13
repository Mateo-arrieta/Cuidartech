from usuarios.models import Paciente, FamiliarPaciente, Usuario

ROL_FAMILIAR = 2


class PacienteRepository:
    """Único lugar que habla con la base de datos para pacientes y sus familiares."""

    # ── Pacientes ──
    def listar(self):
        return Paciente.objects.all()

    def obtener(self, pk):
        return Paciente.objects.filter(pk=pk).first()

    def obtener_de_cuidador(self, id_paciente, id_cuidador):
        return Paciente.objects.filter(
            id_paciente=id_paciente, id_cuidador_id=id_cuidador
        ).first()

    def existe_documento(self, tipo_documento, numero_documento):
        return Paciente.objects.filter(
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
        ).exists()

    def crear(self, **datos):
        return Paciente.objects.create(**datos)

    def actualizar(self, paciente, **datos):
        for campo, valor in datos.items():
            setattr(paciente, campo, valor)
        paciente.save()
        return paciente

    def eliminar(self, paciente):
        paciente.delete()

    # ── Familiares del paciente ──
    def listar_familiares(self, paciente):
        return FamiliarPaciente.objects.filter(
            id_paciente=paciente).select_related('id_familiar')

    def buscar_familiar_por_correo(self, correo):
        return Usuario.objects.filter(correo=correo, id_rol=ROL_FAMILIAR).first()

    def familiar_esta_asignado(self, familiar, paciente):
        return FamiliarPaciente.objects.filter(
            id_familiar=familiar, id_paciente=paciente).exists()

    def asignar_familiar(self, familiar, paciente):
        return FamiliarPaciente.objects.create(
            id_familiar=familiar, id_paciente=paciente)

    def quitar_familiar(self, paciente, id_familiar):
        eliminados, _ = FamiliarPaciente.objects.filter(
            id_paciente=paciente, id_familiar_id=id_familiar).delete()
        return eliminados > 0
from datetime import date, datetime
from ..models import Paciente
from .validadores import ValidadorPaciente

class PacienteInvalidoError(Exception):
    
    def __init__(self, errores):
        self.errores = errores
        super().__init__("; ".join(errores))

class PacienteBuilder:
    
    def __init__(self):
        self.reset()

    def reset(self):
        self._datos = {"estado": True}
        return self

    # ── Pasos de construcción ────────────────────────────────────────────
    def con_datos_personales(self, nombre, apellidos, fecha_nacimiento, sexo):
        self._datos["nombre"] = (nombre or "").strip()
        self._datos["apellidos"] = (apellidos or "").strip()
        self._datos["fecha_nacimiento"] = (fecha_nacimiento or "").strip()
        self._datos["sexo"] = (sexo or "").strip()
        return self

    def con_documento(self, tipo_documento, numero_documento):
        self._datos["tipo_documento"] = (tipo_documento or "").strip()
        self._datos["numero_documento"] = (numero_documento or "").strip()
        return self

    def con_contacto_emergencia(self, contacto):
        self._datos["contacto_emergencia"] = (contacto or "").strip()
        return self

    def con_diagnostico(self, diagnostico):
        self._datos["diagnostico"] = (diagnostico or "").strip()
        return self

    def con_cuidador(self, id_cuidador):
        self._datos["id_cuidador_id"] = id_cuidador
        return self

    # ── Resultado ────────────────────────────────────────────────────────
    def build(self, paciente_existente=None):
       
        excluir_id = paciente_existente.id_paciente if paciente_existente else None
        errores = self._validar(excluir_id)
        if errores:
            raise PacienteInvalidoError(errores)

        if paciente_existente is None:
            paciente = Paciente(**self._datos)
        else:
            paciente = paciente_existente
            for campo, valor in self._datos.items():
                if campo not in ("estado", "id_cuidador_id"):
                    setattr(paciente, campo, valor)

        self.reset()
        return paciente

    # ── Validaciones internas ────────────────────────────────────────────
    def _validar(self, excluir_id=None):
        d = self._datos
        errores = []

        obligatorios = {
            "nombre": "Los nombres",
            "apellidos": "Los apellidos",
            "fecha_nacimiento": "La fecha de nacimiento",
            "sexo": "El sexo",
            "tipo_documento": "El tipo de documento",
            "numero_documento": "El número de documento",
            "contacto_emergencia": "El contacto de emergencia",
            "diagnostico": "El diagnostico del paciente",
        }
        for campo, etiqueta in obligatorios.items():
            if not d.get(campo):
                errores.append(f"{etiqueta} es obligatorio.")

        if not d.get("id_cuidador_id"):
            errores.append("El paciente debe tener un cuidador responsable.")

        if d.get("fecha_nacimiento"):
            try:
                fecha = datetime.strptime(d["fecha_nacimiento"], "%Y-%m-%d").date()
                if fecha > date.today():
                    errores.append("La fecha de nacimiento no puede ser futura.")
                else:
                    d["fecha_nacimiento"] = fecha
            except ValueError:
                errores.append("La fecha de nacimiento no tiene un formato válido.")

        if d.get("tipo_documento") and d.get("numero_documento"):
            fecha = d.get("fecha_nacimiento")
            if not isinstance(fecha, date):
                fecha = None
            errores += ValidadorPaciente().validar(
                d["tipo_documento"], d["numero_documento"], fecha)

            repetidos = Paciente.objects.filter(
                tipo_documento=d["tipo_documento"],
                numero_documento=d["numero_documento"],
            )
            if excluir_id:
                repetidos = repetidos.exclude(id_paciente=excluir_id)
            if repetidos.exists():
                errores.append("Ya existe un paciente con ese documento.")

        return errores
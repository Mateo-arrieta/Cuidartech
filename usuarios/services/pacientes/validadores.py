from abc import ABC, abstractmethod
from datetime import date


def calcular_edad(fecha_nacimiento):
    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )


class ValidadorDocumento(ABC):
    
    @abstractmethod
    def validar(self, numero, fecha_nacimiento):
        """Devuelve una lista de errores (vacía si el documento es válido)."""


class ValidadorCedula(ValidadorDocumento):
    def validar(self, numero, fecha_nacimiento):
        errores = []
        if not (numero.isdigit() and 6 <= len(numero) <= 10):
            errores.append("La cédula debe tener entre 6 y 10 dígitos numéricos.")
        if fecha_nacimiento and calcular_edad(fecha_nacimiento) < 18:
            errores.append("La cédula de ciudadanía solo aplica a mayores de 18 años.")
        return errores


class ValidadorTarjetaIdentidad(ValidadorDocumento):
    def validar(self, numero, fecha_nacimiento):
        errores = []
        if not (numero.isdigit() and len(numero) in (10, 11)):
            errores.append("La tarjeta de identidad debe tener 10 u 11 dígitos numéricos.")
        if fecha_nacimiento and calcular_edad(fecha_nacimiento) >= 18:
            errores.append("La tarjeta de identidad solo aplica a menores de 18 años.")
        return errores


class ValidadorCedulaExtranjeria(ValidadorDocumento):
    def validar(self, numero, fecha_nacimiento):
        errores = []
        if not (numero.isdigit() and 6 <= len(numero) <= 7):
            errores.append("La cédula de extranjería debe tener 6 o 7 dígitos numéricos.")
        return errores


class ValidadorPasaporte(ValidadorDocumento):
    def validar(self, numero, fecha_nacimiento):
        errores = []
        if not (numero.isalnum() and 6 <= len(numero) <= 9):
            errores.append("El pasaporte debe tener entre 6 y 9 caracteres (letras y números).")
        return errores


class ValidadorPaciente:
    """Contexto: elige la estrategia según el tipo de documento y la ejecuta."""

    _estrategias = {
        "CC": ValidadorCedula(),
        "TI": ValidadorTarjetaIdentidad(),
        "CE": ValidadorCedulaExtranjeria(),
        "PA": ValidadorPasaporte(),
    }

    def validar(self, tipo_documento, numero, fecha_nacimiento=None):
        estrategia = self._estrategias.get(tipo_documento)
        if estrategia is None:
            return ["El tipo de documento no es válido."]
        return estrategia.validar(numero, fecha_nacimiento)
class ReglaNegocioError(Exception):
    """Error de regla de negocio. El controlador lo traduce a mensaje o código HTTP."""


class PacienteNoEncontradoError(ReglaNegocioError):
    pass


class FamiliarNoEncontradoError(ReglaNegocioError):
    pass


class FamiliarYaAsignadoError(ReglaNegocioError):
    pass
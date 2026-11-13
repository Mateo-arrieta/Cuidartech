"""
REPOSITORIO DE USUARIOS (capa de datos)
Solo lo necesario para que la API pueda iniciar sesión.
"""
from usuarios.models import Usuario


class UsuarioRepository:

    def buscar_por_correo(self, correo):
        return Usuario.objects.filter(correo=correo).first()
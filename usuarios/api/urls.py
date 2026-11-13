from django.urls import path

from . import views

urlpatterns = [
    path("auth/login/", views.login, name="api_login"),
    path("pacientes/", views.pacientes, name="api_pacientes"),
    path("pacientes/auditoria/", views.auditoria, name="api_auditoria"),
    path("pacientes/<int:id_paciente>/", views.paciente_detalle, name="api_paciente_detalle"),
]
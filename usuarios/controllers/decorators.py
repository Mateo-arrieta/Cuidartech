from functools import wraps
from django.shortcuts import redirect


def solo_cuidador(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            return redirect('login')
        if request.session.get('usuario_rol') != 1:
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
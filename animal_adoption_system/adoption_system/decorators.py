from functools import wraps
from django.shortcuts import redirect


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)

        return redirect('panel_login')   # changed

    return wrapper


def vet_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if request.user.is_authenticated and request.user.groups.filter(name='Vet').exists():
            return view_func(request, *args, **kwargs)

        return redirect('panel_login')   # changed

    return wrapper


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if request.user.is_authenticated and request.user.groups.filter(name='Staff').exists():
            return view_func(request, *args, **kwargs)

        return redirect('panel_login')   # changed

    return wrapper
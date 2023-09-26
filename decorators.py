from django.shortcuts import render, redirect
from .models import FactoryOwner  # Asegúrate de importar el modelo FactoryOwner

def factory_owner_required(view_func):
    def wrap(request, *args, **kwargs):
        try:
            request.user.factory_owner  # Utiliza el nombre correcto del campo aquí
        except FactoryOwner.DoesNotExist:  # Si no existe, redirige al usuario a una página de error o de inicio de sesión
            return redirect('name_of_your_login_url')
        return view_func(request, *args, **kwargs)  # Si existe, simplemente llama a la función de vista original
    return wrap

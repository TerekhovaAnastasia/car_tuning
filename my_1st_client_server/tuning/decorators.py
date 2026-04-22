from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def superuser_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'У вас нет прав доступа к этой странице')
        return redirect('admin_panel')
    return _wrapped_view

def user_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'У вас нет прав доступа к этой странице')
        return redirect('home')
    return _wrapped_view

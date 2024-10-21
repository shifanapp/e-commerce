from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def login_required_message(function=None, redirect_field_name='/login/', message=None):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f'{redirect_field_name}?next={request.path}')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    if function:
        return decorator(function)
    return decorator

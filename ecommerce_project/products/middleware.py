# middleware.py

from django.shortcuts import redirect
from django.urls import reverse

class PreventBackToLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If user is authenticated and trying to access the login page, redirect to home
        if request.user.is_authenticated and request.path == reverse('login'):
            return redirect(reverse('home'))
        return self.get_response(request)

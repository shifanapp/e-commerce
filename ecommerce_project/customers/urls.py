"""
URL configuration for ecommerce_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.login_view, name='login'),
        path('register',views.register,name='register'),
        path('logout',views.logout_view,name='logout'),
        # path('my_account',views.account_view,name='my_account'),
        path('change_password/', views.change_password, name='change_password'),
        path('my_account', views.my_account, name='my_account'),
        path('login_prompt',views.login_prompt_view,name='login_prompt'),
        path('activate/<uidb64>/<token>/', views.activate, name='activate'),
        path('forgot_password/', views.forgot_password, name='forgot_password'),
# path('change_password/', change_password, name='change_password'),
          path('password_reset/', views.password_reset_request, name='password_reset'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password_reset_done/', views.password_reset_done, name='password_reset_done'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
    path('update_account/', views.update_account, name='update_account'),
    # path('manage_addresses/', views.manage_addresses, name='manage_addresses'),
    path('manage-addresses/', views.manage_addresses, name='manage_addresses'),


    ]
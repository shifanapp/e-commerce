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
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from .views import *
urlpatterns = [
    path('',admin_login,name="admin_login"),
    path('logout',logout_view,name='logout'),

    path('dashboard/',dashboard,name="dashboard"),
    path('products/', product_module, name='product_list'),
    path('products/add/', add_product, name='add_product'),
    path('products/edit/<pk>', edit_product, name='edit_product'),
    path('products/delete/<pk>', delete_product, name='delete_product'),
    path('products/restore/<pk>', restore_product, name='restore_product'),
    
    path('orders/', order_module, name='orders_list'),
    path('edit-order/<int:order_id>/', edit_order, name='edit_order'),
    path('add_order/', add_order, name='add_order'),
    path('delete_order/<int:id>/', delete_order, name='delete_order'),
    path('coupons/', coupon_list, name='coupon_list'),
    path('coupons/add/', add_coupon, name='add_coupon'),
    path('coupons/edit/<int:pk>/', edit_coupon, name='edit_coupon'),
    path('coupon/delete/<int:pk>/', delete_coupon, name='delete_coupon'),

    path('users/', user_list, name='user_list'),
    path('users/add/', user_add, name='user_add'),
    path('users/edit/<pk>', user_edit, name='user_edit'),
    path('users/delete/<pk>', user_delete, name='user_delete'),
    # path('user-registration-stats/', user_registration_stats, name='user_registration_stats'),







]
urlpatterns +=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


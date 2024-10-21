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
urlpatterns = [
        path('', views.index,name='home'),
        path('category/<str:category_name>/', views.category_view, name='category_view'),
        path('product_list',views.list_product,name='list_product'),
        path('product_details/<pk>',views.product_detail,name='product_detail'),
        path('wishlist/', views.wishlist, name='wishlist'),
        path('add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
        # path('search/', views.search, name='search'),
        path('remove-from-wishlist', views.remove_from_wishlist, name='remove_from_wishlist'),
        path('wishlist/empty/', views.wishlist_empty_view, name='wishlist_empty'),
        path('list_of_product/', views.list_of_product, name='list_of_product'),



        
]



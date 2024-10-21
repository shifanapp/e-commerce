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
        path('cart',views.show_cart,name='cart'),
        path('add_to_cart',views.add_to_cart,name='add_to_cart'),
        path('remove_item/<pk>',views.remove_item_from_cart,name='remove_item_from_cart'),
        path('checkout',views.checkout_cart,name='checkout'),
        # path('payment',views.payment,name='payment'),
        
        # path('payment/success/', views.payment_success, name='payment_success'),
        # path('payment/failed/', views.payment_failed, name='payment_failed'),
        path('orders',views.show_orders,name='orders'),
        path('empty_cart',views.empty_cart,name='empty_cart'),
        path('login_prompt',views.login_prompt_view,name='login_prompt'),
        # path('login/', views.custom_login_view, name='login'),
        path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
        path('remove_coupon/', views.remove_coupon, name='remove_coupon'),
        path('create-order/', views.create_order, name='create_order'),
        path('verify-payment/', views.PaymentVerificationView.as_view(), name='verify_payment'),
        # path('payment-success/', views.payment_success, name='payment_success'),
        path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
        # path('order/order/buy-now/<int:product_id>/create-order/',views.create_order,name='create_order'),
            path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
        path('order/<int:order_id>/', views.order_view, name='order_view'),
    # path('invoice/view/<int:order_id>/', views.invoice_view, name='invoice_view'),
    # path('invoice/<int:order_id>/', views.invoice, name='invoice'),
    path('invoice/view/<int:order_id>/', views.generate_invoice_pdf, name='view_invoice_pdf'),
        path('add_address/', views.add_address, name='add_address'),


            # path('invoice/<int:order_id>/', views.generate_invoice_pdf, name='generate_invoice_pdf'),


            






        
        


        
]



from django.contrib import admin
from . models import Order,OrderItem,Payment,Cart
# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_filter=[
        "owner",
        "status",
    ]
    search_fields=(
        "owner",
        "id"
    )
    list_display=['id','owner','status','total_price']
    
class orderitemAdmin(admin.ModelAdmin):
    list_display=['id','user','product','quantity']

class cartAdmin(admin.ModelAdmin):
    list_display=['id','cart_user']

    
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderItem,orderitemAdmin)
admin.site.register(Payment)
# admin.site.register(Cart,cartAdmin)y




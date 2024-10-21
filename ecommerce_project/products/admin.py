from django.contrib import admin
from . models import Product,Category,Wishlist,Coupon,SubCategory,Review,Size
# Register your models here.

class productAdmin(admin.ModelAdmin):
    list_display=['id','name','price','category',]
    

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug')
    list_filter = ('category',)
    
class reviewAdmin(admin.ModelAdmin):
    list_display=['id','product','user','comment','rating']
  
admin.site.register(Product,productAdmin)
admin.site.register(Category)
admin.site.register(Wishlist)
admin.site.register(Coupon)
admin.site.register(Review,reviewAdmin)
admin.site.register(Size)






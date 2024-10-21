from django.db import models
from django.contrib.auth.models import User,AbstractUser


# Model for product

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted_status=Product.LIVE)

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db).active()
class Size(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    # Other fields if needed

    def __str__(self):
        return self.name  
class Product(models.Model):
    LIVE=1
    DELETE=0
    DELETE_CHOICES=((LIVE,'Live'),(DELETE,'delete'))
    name=models.CharField(max_length=200)
    description=models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image_url = models.ImageField(upload_to='media')
    image_1 = models.ImageField(upload_to='media',default="null",null=True)
    image_2 = models.ImageField(upload_to='media',default="null",null=True)
    image_3 = models.ImageField(upload_to='media',default="null",null=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, related_name='sub_products', on_delete=models.CASCADE,default=1)
    sizes = models.ManyToManyField(Size)  # Many-to-Many relationship for multiple sizes
    priority=models.IntegerField(default=0)
    deleted_status=models.IntegerField(choices=DELETE_CHOICES,default=LIVE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
     
    objects = ProductManager()  # Attach the custom manager here

    def __str__(self):
        return self.name
    
    def soft_delete(self):
        self.deleted_status = self.DELETE
        self.save()

    def restore(self):
        self.deleted_status = self.LIVE
        self.save()
        
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'product')  # Ensure each user can add a product to the wishlist only once

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class Coupon(models.Model):
    coupon_code=models.CharField(max_length=10)
    is_expired=models.BooleanField(default=False)
    discount_price=models.IntegerField(default=100)  
    minimum_amount=models.IntegerField(default=500)
    def __str__(self):
        return self.coupon_code
    
class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # Rating from 1 to 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    images = models.ImageField(upload_to='review_images/', blank=True, null=True)
    helpful_count = models.PositiveIntegerField(default=0)
    not_helpful_count = models.PositiveIntegerField(default=0)
    fabric_quality = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True)
    comfort = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True)
    style = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True)
    def __str__(self):
        return self.comment
    
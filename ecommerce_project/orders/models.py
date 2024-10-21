from django.db import models
from django.contrib.auth.models import User
from products.models import Product, Coupon
from customers.models import Profile,Address
from django.utils import timezone

# Model for Order
class Order(models.Model):
    LIVE = 1
    DELETE = 0
    DELETE_CHOICES = ((LIVE, 'Live'), (DELETE, 'Delete'))
    
    CART_STAGE = 0
    ORDER_CONFIRMED = 1
    ORDER_PROCESSED = 2
    ORDER_DELIVERED = 3
    ORDER_REJECTED = 4
    STATUS_CHOICES = (
        (CART_STAGE, "CART_STAGE"),
        (ORDER_CONFIRMED, "ORDER_CONFIRMED"),
        (ORDER_PROCESSED, "ORDER_PROCESSED"),
        (ORDER_DELIVERED, "ORDER_DELIVERED"),
        (ORDER_REJECTED, "ORDER_REJECTED"),
    )

    owner = models.ForeignKey(Profile, related_name='orders', on_delete=models.SET_NULL, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=CART_STAGE)
    total_price = models.FloatField(default=0)
    deleted_status = models.IntegerField(choices=DELETE_CHOICES, default=LIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # order_id = models.CharField(max_length=100)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)  # Add the address field here


    def __str__(self):
        return f'Order {self.id} by {self.owner.user}'
    def calculate_total_price(self):
        # Assuming there's a related model 'OrderItem' that links to this Order
        self.total_price = sum(item.price * item.quantity for item in self.added_items.all())
        self.save()
        return self.total_price

# Model for Payment
class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment',null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=100, unique=True,null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    amount = models.FloatField()
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"Payment for Order {self.order.id}"
    
# Model for Cart
class Cart(models.Model):
    cart_user = models.ForeignKey(User, related_name='cart', on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.cart_user.username}\'s cart'
    def get_subtotal(self):
        """
        Returns the subtotal before any discounts (only for active items).
        """
        subtotal = sum([item.get_total_price() for item in self.items.filter(is_active=True)])
        return subtotal

    def get_total(self):
        """
        Returns the total after applying coupons (only for active items).
        """
        total = sum([item.get_discounted_price() for item in self.items.filter(is_active=True)])
        return total

    def get_total_savings(self):
        """
        Returns the total savings from applied coupons (only for active items).
        """
        savings = sum([item.get_savings() for item in self.items.filter(is_active=True)])
        return savings
    
    def get_cart_total(cart):
        cartitems = CartItem.objects.filter(cart=cart, is_active=True)
        total = 0
        for item in cartitems:
            total += item.product.price * item.quantity
        print("TOTAL==============",total)
        return total
        
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)  # Soft delete flag
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    
    def get_total_price(self):
        """
        Returns the total price for this item before applying any coupon.
        """
        return self.product.price * self.quantity

    def get_discounted_price(self):
        """
        Returns the price after applying the coupon (if any).
        """
        total_price = self.get_total_price()
        if self.coupon:
            # If it's a flat discount, apply it
            return max(total_price - self.coupon.discount_price, 0)
        return total_price

    def get_savings(self):
        """
        Returns the savings due to coupon application.
        """
        if self.coupon:
            return self.coupon.discount_price * self.quantity
        return 0
    # class Meta:
    #     unique_together = ('cart', 'product')
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"    
    def get_cart_total(self):
        total = sum(item.get_subtotal() for item in self.items.all())
        return total
    def get_subtotal(self):
        return self.product.price * self.quantity
# Model for OrderItem
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='added_items', on_delete=models.SET_NULL, null=True)
    # cart = models.ForeignKey(Cart, related_name='items',null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, related_name='added_carts', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} of {self.product.name}'
    def get_subtotal(self):
        return self.product.price * self.quantity

class Invoice(models.Model):
    invoice_number = models.CharField(max_length=100, unique=True)
    order = models.OneToOneField('Order', on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer.username}"
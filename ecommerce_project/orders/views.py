from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.conf import settings
import razorpay
from .models import Order, OrderItem, Payment, Cart, CartItem
from products.models import Product, Coupon
from customers.models import Address
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
import logging
from django.utils import timezone



# Create a Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        user = request.user
        quantity = int(request.POST.get('quantity'))
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        cart_item, _ = Cart.objects.get_or_create(cart_user=user)
        cart, created = CartItem.objects.get_or_create(cart=cart_item,quantity=quantity, product=product,is_active=True)
        if created:
            message = 'Product added to cart successfully!'
            response_status = 200
        else:
            message = 'Product is already in your Cart.'
            response_status = 400
        cart_count = CartItem.objects.filter(cart=cart_item,is_active=True).count()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
             return JsonResponse({'message': message, 'cart_count': cart_count}, status=response_status)
        else:
            if response_status == 200:
                messages.success(request, message)
            else:
                messages.error(request, message)
            return redirect('product_detail', pk=product_id)
    return redirect('/customer/login_prompt/')

@login_required
def checkout_cart(request):
    user = request.user
    customer = user.customer_profile
    cart = Cart.objects.get(cart_user=user)
    cart_items = cart.items.filter(is_active=True)  # Get only active items
    addresses = Address.objects.filter(user=user)

    if request.method == 'POST':
        if cart:
            subtotal = cart.get_subtotal()
            total = cart.get_total()
            total_savings = cart.get_total_savings()
        else:
            subtotal = total = total_savings = 0
        print("TOTAL=========",total)

        print("SUBTOTAL=========",subtotal)
        # Check if there are no items in the cart
        if subtotal <= 0:
            messages.error(request, 'Your cart is empty.')
            return redirect('cart')  # Adjust this URL name based on your URLs configuration
        address_id = request.POST.get('address_id')

        print("ADDRESSS======",address_id)

        # Create the order
        order = Order.objects.create(
            owner=customer,
            status=Order.ORDER_CONFIRMED,
            total_price=total,
        )

        # Create OrderItems from CartItems and mark them as inactive
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
            )
            item.is_active = False  # Mark cart item as inactive
            item.save()

        # Create a Razorpay order
        amount = total * 100  # Convert amount to paise
        currency = 'INR'
        print("Creating order with currency:", currency)

        # Use your Razorpay client to create the order
        razorpay_order = client.order.create({
            'amount': int(amount),
            'currency': currency,
            'payment_capture': '1'
        })

        # Create or get the payment record for this order
        payment, _ = Payment.objects.get_or_create(
            order=order,
            defaults={
                'razorpay_order_id': razorpay_order['id'],
                'amount': amount
            }
        )

        # Pass the Razorpay order details to the template
        return render(request, 'checkout.html', {
            'order_items': order.added_items.all(),  # Pass OrderItems instead of CartItems
            'addresses': addresses,
            'subtotal': subtotal,
            'total': total,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_amount': amount,
            'razorpay_currency': currency,
            'razorpay_key': settings.RAZORPAY_API_KEY,  # Make sure to add this to your settings
        })

    # For GET requests, just render the checkout page without creating an order
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'addresses': addresses,
        'subtotal': sum(item.get_subtotal() for item in cart_items),  # Recalculate subtotal for GET request
        'total': cart.get_cart_total(),
    })


@login_required
def show_orders(request):
    customer = request.user.customer_profile
    all_orders = Order.objects.filter(owner=customer)
    for order in all_orders:
        order.local_created_at = timezone.localtime(order.created_at)
    context = {'orders': all_orders,'order.local_created_at':order.local_created_at}
    return render(request, 'orders.html', context)
from decimal import Decimal
@login_required
def apply_coupon(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        coupon_code = request.POST.get('coupon_code')
        try:
            cart = Cart.objects.get(cart_user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)  # Get all cart items associated with the cart
            coupon = Coupon.objects.get(coupon_code=coupon_code)

            # Check if coupon is expired
            if coupon.is_expired:
                return JsonResponse({'success': False, 'message': 'This coupon has expired.'})
            
            # Check if the total cart value is less than the coupon's minimum amount
            cart_total = Decimal(cart.get_cart_total())  # Ensure cart_total is a Decimal
            if cart_total < coupon.minimum_amount:
                return JsonResponse({'success': False, 'message': f'This coupon requires a minimum purchase of ${coupon.minimum_amount}.'})
            
            # Check if any cart item already has the coupon applied
            if any(item.coupon == coupon for item in cart_items):
                return JsonResponse({'success': False, 'message': 'This coupon is already applied.'})
            
            # Apply the coupon to all cart items
            for cart_item in cart_items:
                cart_item.coupon = coupon
                cart_item.save()

            discount_amount = Decimal(coupon.discount_price)  # Ensure discount_amount is a Decimal
            discounted_total = cart_total - discount_amount  # Both are Decimal now, so this will work

            return JsonResponse({
                'success': True,
                'message': 'Coupon applied successfully.',
                'cart_total': discounted_total,
                'discount_amount': discount_amount
            })

        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid coupon code.'})
        except Cart.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No cart found for the user.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})


@require_POST
@login_required
def remove_coupon(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            cart = Cart.objects.get(cart_user=request.user)
            cart_items = cart.items.all()  # Retrieve all cart items related to the cart

            # Remove the coupon from each cart item
            for cartitem in cart_items:
                cartitem.coupon = None
                cartitem.save()

            # Recalculate the cart total after removing the coupon
            cart_total = float(cart.get_cart_total())

            return JsonResponse({'success': True, 'message': 'Coupon removed successfully.', 'cart_total': cart_total})
        
        except Cart.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No cart found for the user.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})



@login_required
def show_cart(request):
    cart_count = CartItem.objects.filter(is_active=True).count()
    if cart_count == 0:
        return redirect('empty_cart')  # Redirect to empty wishlist page

    if request.user.is_authenticated:
        if cart_count == 0:
            return redirect('empty_cart')
        else:
            cart, _ = Cart.objects.get_or_create(cart_user=request.user)
            cart_items = CartItem.objects.filter(is_active=True)
            subtotal = sum(item.get_subtotal() for item in cart_items)
            cart_total = cart.get_cart_total()  # Total after discounts
            print("CART_TOTAL====",cart_total)
            context = {
                'cart': cart,
                'cart_items': cart_items,
                'subtotal': subtotal,
                'cart_total': cart_total,
                'cart_count' : cart_count
            }
            return render(request, 'cart.html', context)
    else:
        return redirect('/customer/login_prompt/')



def remove_item_from_cart(request, pk):
    if request.method == 'POST':
        try:
            # Retrieve the cart item or return a 404 if not found
            cart_item = get_object_or_404(CartItem, pk=pk)
            print("CARTITEM======",cart_item)
            # Set the item as inactive or delete it, depending on your model design
            # cart_item.delete()  # Use this if you want to delete the item entirely

            # Alternatively, if you want to just mark it as inactive:
            cart_item.is_active = False
            cart_item.save()
            cart_count = CartItem.objects.filter(is_active=True).count()
            cart_items = CartItem.objects.filter(is_active=True)

            subtotal = sum(item.get_subtotal() for item in cart_items)
            if not cart_items.exists():
                subtotal = 0
            # Respond with success
            return JsonResponse({'success': True,'cart_count':cart_count,'subtotal':subtotal})
        except CartItem.DoesNotExist:
            # Specific error if the item does not exist
            return JsonResponse({'success': False, 'error': 'Cart item does not exist.'})
        except Exception as e:
            # General error handling
            return JsonResponse({'success': False, 'error': str(e)})

    # If the request method is not POST, return an error
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required
def create_order(request):
    user = request.user
    customer = user.customer_profile

    # Retrieve the confirmed order for the customer
    try:
        order = Order.objects.get(owner=customer, status=Order.ORDER_CONFIRMED)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found or not confirmed.'}, status=404)

    # Retrieve the associated order items
    order_items = order.added_items.all()  # Assuming 'items' is the related name in Order for OrderItems
    
    # Calculate the total amount from order items
    total_amount = sum(item.get_subtotal() for item in order_items)  # Assuming get_subtotal() exists in OrderItem
    print("total_amount=", total_amount)

    # If total amount is zero, return an error
    if total_amount <= 0:
        return JsonResponse({'error': 'Total amount cannot be zero.'}, status=400)

    amount = total_amount * 100  # Amount in paise
    currency = 'INR'

    # Create an order in Razorpay
    razorpay_order = client.order.create({
        'amount': int(amount),
        'currency': currency,
        'payment_capture': '1'
    })
    
    # Create or get the payment record for this order
    payment, _ = Payment.objects.get_or_create(
        order=order,
        defaults={
            'razorpay_order_id': razorpay_order['id'],
            'amount': amount
        }
    )
    print("razorpay_order_id=", razorpay_order['id'])

    # Return the Razorpay order details in the response
    return JsonResponse({
        'order_id': razorpay_order['id'],
        'amount': amount,
        'currency': currency
    })


@method_decorator(csrf_exempt, name='dispatch')
class PaymentVerificationView(View):
    def post(self, request, *args, **kwargs):
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')
        address_id = request.POST.get('address_id')  # Get the selected address ID

        print("ADDRESSS======",address_id)
        try:
            # Verify the payment signature using Razorpay's utility
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
            selected_address = Address.objects.get(id=address_id)

            # Retrieve the user's cart
            cart = Cart.objects.get(cart_user=request.user)
            customer = request.user.customer_profile

            # Retrieve all confirmed orders for the user (could be single or multiple)
            confirmed_orders = Order.objects.filter(owner=customer, status=Order.ORDER_CONFIRMED)

            if confirmed_orders.exists():
                if confirmed_orders.count() == 1:
                    # Single order scenario
                    order = confirmed_orders.first()
                    order.status = Order.ORDER_PROCESSED
                    order.address=selected_address

                    order.save()
                else:
                    # Multiple orders scenario - choose how to handle this
                    # Option 1: Process all confirmed orders
                    for order in confirmed_orders:
                        order.status = Order.ORDER_PROCESSED
                        order.address=selected_address

                        order.save()

                    # Option 2: Only process the most recent confirmed order
                    # order = confirmed_orders.latest('created_at')  # Assuming 'created_at' exists

                # Soft delete items in the cart (Optional: Check if this step is needed)
                for item in cart.items.all():
                    item.is_active = False
                    item.save()

                # Update the payment record
                payment = Payment.objects.get(razorpay_order_id=order_id)
                payment.razorpay_payment_id = payment_id
                payment.razorpay_signature = signature
                payment.status = 'Success'
                payment.save()

                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'failure', 'error': 'No confirmed orders found'})
        
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'status': 'failure', 'error': 'Signature verification failed'})

        except Order.DoesNotExist:
            return JsonResponse({'status': 'failure', 'error': 'Order does not exist'})

        except Payment.DoesNotExist:
            return JsonResponse({'status': 'failure', 'error': 'Payment not found'})

        except Exception as e:
            return JsonResponse({'status': 'failure', 'error': str(e)})

def empty_cart(request):
    return render (request,'cart_empty.html') 

def login_prompt_view(request):
    return render (request,'login_prompt.html')

# buy now option
@login_required
def buy_now(request, product_id):
    if request.method == 'POST':

        user = request.user
        customer = user.customer_profile
        cart = Cart.objects.get(cart_user=user)
        cart_items = cart.items.filter(is_active=True)  # Get only active items
        addresses = Address.objects.filter(user=user)
        product_price = request.POST.get('product_price')
        product = get_object_or_404(Product, id=product_id)
        # product = request.POST.get('buy_now')

        print("product_price=",product_price)
        if request.method == 'POST':
            # Calculate subtotal and total
            subtotal = sum(item.get_subtotal() for item in cart_items)
            total = cart.get_cart_total()

            # Check if there are no items in the cart
            # if subtotal <= 0:
            #     messages.error(request, 'Your cart is empty.')
            #     return redirect('cart')  # Adjust this URL name based on your URLs configuration

            # Create the order
            order = Order.objects.create(
                owner=customer,
                status=Order.ORDER_CONFIRMED,
                total_price=product_price,
            )

            # Create OrderItems from CartItems and mark them as inactive
            order_item, created = OrderItem.objects.get_or_create(
            order=order,
            product=product,
            quantity= 1  # Defaults only used if creating new
            )
            if not created:
            # If the order item already exists, just increase the quantity
                order_item.quantity += 1
                order_item.save()    

            # Create a Razorpay order
            amount = int(float(product_price) )    # Convert amount to paise
            currency = 'INR'
            print("Creating order with currency:", order)

            # Use your Razorpay client to create the order
            razorpay_order = client.order.create({
                'amount': int(amount)* 100,
                'currency': currency,
                'payment_capture': '1'
            })

            # Create or get the payment record for this order
            payment, _ = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'razorpay_order_id': razorpay_order['id'],
                    'amount': amount
                }
            )

            # Pass the Razorpay order details to the template
            return render(request, 'checkout.html', {
                'order_items': order.added_items.all(),  # Pass OrderItems instead of CartItems
                'addresses': addresses,
                'subtotal': subtotal,
                'total': total,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_amount': amount,
                'razorpay_currency': currency,
                'razorpay_key': settings.RAZORPAY_API_KEY,  # Make sure to add this to your settings
            })

        # For GET requests, just render the checkout page without creating an order
        return render(request, 'checkout.html', {
            'cart_items': cart_items,
            'addresses': addresses,
            'subtotal': sum(item.get_subtotal() for item in cart_items),  # Recalculate subtotal for GET request
            'total': cart.get_cart_total(),
        })

@require_POST
def update_cart_quantity(request):
    if request.method == 'POST':
        cart_id = request.POST.get('cart_id')
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))

        cart = Cart.objects.get(id=cart_id)
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id,is_active=True)

        cart_item.quantity = quantity
        cart_item.save()

        # Recalculate total price and ensure it is a float
        cart_items = cart.items.filter(is_active=True)  # Get only active items

        # Recalculate total price for all items in the cart
        total_price = sum(item.get_subtotal() for item in cart_items)
        item_total = cart_item.get_total_price()


        return JsonResponse({
            'success': True,
            'total_price': total_price,  # Ensure this is a float
            'item_total':item_total
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

# views.py

def order_view(request, order_id):
    user = request.user
    order = get_object_or_404(Order, id=order_id)
    order_items = order.added_items.all()
    local_time = timezone.localtime(order.created_at)  # Convert to local time

    address = order.address 
    context = {
        'order': order,
        'order_items': order_items,
        'address':address,
        'local_time': local_time,

    }
    return render(request, 'order_view.html', context)

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import Order  # Assuming you have an Order model
from reportlab.pdfgen import canvas


from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from datetime import datetime
@xframe_options_exempt
def generate_invoice_pdf(request, order_id):
    print("Generating PDF for Order:", order_id)
    
    # Get the order object
    order = get_object_or_404(Order, id=order_id)
    
    # Create a BytesIO buffer to receive the PDF data
    buffer = BytesIO()
    
    # Create a PDF object using ReportLab
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Set margins and title
    margin_x = 100
    margin_y = 50
    
    # Add title to the PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(margin_x, height - margin_y, f"Invoice for Order ID: {order.id}")
    
    # Order details section with some spacing
    p.setFont("Helvetica", 12)
    p.drawString(margin_x, height - (margin_y + 30), f"Order ID: {order.id}")
    p.drawString(margin_x, height - (margin_y + 60), f"Date: {order.created_at.strftime('%d %B, %Y')}")
    p.drawString(margin_x, height - (margin_y + 90), f"Total Price: ₹{order.total_price:.2f}")

    # Customer details
    # p.drawString(margin_x, height - (margin_y + 120), f"Customer: {order.user.get_full_name()}")
    # p.drawString(margin_x, height - (margin_y + 140), f"Email: {order.user.email}")aq

    # Add a table for order items
    p.setFont("Helvetica-Bold", 14)
    p.drawString(margin_x, height - (margin_y + 180), "Order Items:")
    
    items = order.added_items.all()

    if items:
        # Prepare data for the table
        data = [["Product", "Quantity", "Price"]]
        
        for item in items:
            data.append([str(item.product), str(item.quantity), f"₹{item.product.price * item.quantity:.2f}"])

        # Create a table with items
        table = Table(data, colWidths=[3 * inch, 1 * inch, 1.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Determine the height for the table and dynamically position it
        table_height = len(data) * 20  # Approximate height of the table
        table.wrapOn(p, width, height)
        table.drawOn(p, margin_x, height - (margin_y + 200 + table_height))

    else:
        p.drawString(margin_x, height - (margin_y + 200), "No items available.")

    # Optionally, you can add a footer or more sections like shipping details, payment status, etc.

    # Finalize the PDF
    p.showPage()
    p.save()
    
    # Get the PDF data from the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Return the PDF as an HTTP response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="invoice_{order_id}.pdf"'
    
    return response

logger = logging.getLogger(__name__)

def add_address(request):
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            address_id = request.POST.get('address_id')

            line1 = request.POST.get('line1')
            line2 = request.POST.get('line2')
            city = request.POST.get('city')
            state = request.POST.get('state')
            country = request.POST.get('country')
            zip_code = request.POST.get('zip_code')
            phone_number = request.POST.get('phone_number')
            is_default = request.POST.get('is_default') == 'on'

            logger.debug(f"Action: {action}")
            logger.debug(f"Address ID: {address_id}")
            
            if action == 'add':
                print("ADD========",address_id)
                new_address = Address.objects.create(
                    user=request.user,
                    line1=line1,
                    line2=line2,
                    city=city,
                    state=state,
                    country=country,
                    zip_code=zip_code,
                    phone_number=phone_number,
                    is_default=is_default
                )
                address_data = {
                    'id': new_address.id,
                    'line1': new_address.line1,
                    'line2': new_address.line2,
                    'city': new_address.city,
                    'state': new_address.state,
                    'country': new_address.country,
                    'zip_code': new_address.zip_code,
                    'phone_number': new_address.phone_number,
                    'is_default': new_address.is_default,
                }
                return JsonResponse({'message': 'Address added successfully!', 'address': address_data})

                
        except Exception as e:
            logger.error(f"Error processing form: {e}")
            return JsonResponse({'error': str(e)}, status=400)

    addresses = Address.objects.filter(user=request.user)
    return render(request, 'checkout.html', {'addresses': addresses})


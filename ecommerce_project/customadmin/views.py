from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from products.models import * 
from django.http import JsonResponse
from orders.models import Order,OrderItem,Coupon
from customers.models import Profile
from django.db.models import Sum
from django.utils import timezone
from django.views.decorators.http import require_POST

from products.models import Product, Category
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here
def admin_login(request):
    try:
        if request.method == "POST":
            username = request.POST.get('username')
            print(username)
            password = request.POST.get('password')
            user_obj = User.objects.filter(username=username)
            if not user_obj.exists():
                messages.error(request, 'Account not found')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            user_obj = authenticate(request, username=username, password=password)
            if user_obj and user_obj.is_superuser:
                login(request, user_obj)
                return redirect('dashboard')
            messages.info(request, 'Invalid password')
        return render(request, 'customlogin.html')
    except Exception as e:
        print(e)
        messages.error(request, 'An unexpected error occurred')
        return render(request, 'customlogin.html')
def logout_view(request):
    request.session['has_logged_in'] = False
    logout(request)
    return redirect('home') 

def dashboard(request):
    # Default time period to daily
    period = request.GET.get('period', 'daily')
    all_products = Product.objects.count()
    all_categories = Category.objects.count()
    monthly_earning= Order.objects.filter(deleted_status=Order.LIVE).values('created_at__year', 'created_at__month').annotate(total_sales=Sum('total_price')).order_by('created_at__year', 'created_at__month')
    revenue = Order.objects.filter(deleted_status=Order.LIVE).values('created_at__year').annotate(total_sales=Sum('total_price')).order_by('created_at__year')

    total_order_count=Order.objects.count()
    # Get sales data based on the selected period
    now = timezone.now()
    if period == 'monthly':
        sales_data = Order.objects.filter(deleted_status=Order.LIVE).values('created_at__year', 'created_at__month').annotate(total_sales=Sum('total_price')).order_by('created_at__year', 'created_at__month')
        labels = [f"{entry['created_at__month']}/{entry['created_at__year']}" for entry in sales_data]
    elif period == 'yearly':
        sales_data = Order.objects.filter(deleted_status=Order.LIVE).values('created_at__year').annotate(total_sales=Sum('total_price')).order_by('created_at__year')
        labels = [entry['created_at__year'] for entry in sales_data]
    else:  # Default to daily
        sales_data = Order.objects.filter(deleted_status=Order.LIVE).values('created_at__date').annotate(total_sales=Sum('total_price')).order_by('created_at__date')
        labels = [entry['created_at__date'].strftime('%Y-%m-%d') for entry in sales_data]

    sales = [entry['total_sales'] for entry in sales_data]

    context = {
        "sales_dates": labels,
        "sales_values": sales,
        "current_period": period,
        "all_products":all_products,
        "revenue":revenue,
        "monthly_earning":monthly_earning,
        "total_order_count":total_order_count
    }
    return render(request, 'customadmin/dashboard.html', context)

def product_module(request):
    product_objs=Product.objects.all().order_by("-id")
    return render(request,'customadmin/product.html',{'product_objs':product_objs})

def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image_url = request.FILES.get('image_url')
        image_1 = request.FILES.get('image_1')
        image_2 = request.FILES.get('image_2')
        image_3 = request.FILES.get('image_3')
        category_id = request.POST['category']
        category = Category.objects.get(id=category_id)
        priority = request.POST.get('priority', None)  # Use .get() to avoid the error
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            image_url=image_url,
            image_1=image_1,
            image_2=image_2,
            image_3=image_3,
            category=category,
            priority=priority
        )
        product.save()
        return redirect('products')
    categories = Category.objects.all()
    return render(request, 'customadmin/add_product.html', {'categories': categories})

def edit_product(request,pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')        
        category_id = request.POST.get('category')
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            product.category = category        
        product.priority = request.POST.get('priority')
        if request.FILES.get('image_url'):
            product.image_url = request.FILES['image_url']
        if request.FILES.get('image_1'):
            product.image1 = request.FILES['image_1']
        if request.FILES.get('image_2'):
            product.image2 = request.FILES['image_2']
        if request.FILES.get('image_3'):
            product.image3 = request.FILES['image_3']
        product.save()
        return redirect('products')
    categories = Category.objects.all()
    return render(request, 'customadmin/edit_product.html', {'product': product,'categories': categories})

def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.soft_delete()  # Assume this method sets the product as deleted
        return redirect('product_list')
    return render(request, 'customadmin/confirm_delete_product.html', {'product': product})

def restore_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.restore()
    return redirect('products')

#Order module
def order_module(request):
    order_objs=Order.objects.filter(deleted_status=1).order_by("-id")
    # order_objs=order.objects.all().
    return render(request,'customadmin/order_list.html',{'order_objs':order_objs})

def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)  # Get the order object by ID

    if request.method == 'POST':
        # Manually update fields from the POST request
        owner_id = request.POST.get('owner')
        status = request.POST.get('status')
        total_price = request.POST.get('total_price')

        # Assuming the owner is a ForeignKey, you need to get the owner object if it is editable
        if owner_id:
            order.owner_id = owner_id  # Update the owner (if allowed)

        order.status = status
        order.total_price = total_price
        order.save()  # Save the updated order

        return redirect('orders_list')  # Redirect to the order list after saving

    context = {
        'order': order,
    }
    return render(request, 'customadmin/edit_order.html', context)

def add_order(request):
    if request.method == 'POST':
        owner_id = request.POST.get('owner')
        status = request.POST.get('status')
        total_price = request.POST.get('total_price')
        
        Order.objects.create(
            owner_id=owner_id,
            status=status,
            total_price=total_price
        )
        return redirect('orders_list')  # Redirect to the list of orders or another appropriate page

    profiles = Profile.objects.all()
    return render(request, 'customadmin/add_order.html', {
        'profiles': profiles,
        'order': Order()  # Provide an instance for STATUS_CHOICES in the template
    })
def delete_order(request, id):
    order = get_object_or_404(Order, id=id)
    
    if request.method == 'POST':
        # Optionally, handle related data if necessary
        # For example, delete related order items if needed
        # order.orderitems.all().delete()
        
        # Soft delete (mark as deleted)
        order.deleted_status = Order.DELETE
        order.save()
        
        messages.success(request, 'Order successfully deleted.')
        return redirect('orders_list')  # Redirect to orders list or another page
    
    return render(request, 'customadmin/confirm_delete_order.html', {'order': order})

#coupon module
def coupon_list(request):
    coupons=Coupon.objects.all()
    # order_objs=order.objects.all().
    return render(request,'customadmin/coupon_list.html',{'coupons':coupons})

def add_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        discount_price = request.POST.get('discount_price')
        minimum_amount = request.POST.get('minimum_amount')
        is_expired = request.POST.get('is_expired') == 'on'

        # Create and save the new coupon
        Coupon.objects.create(
            coupon_code=coupon_code,
            discount_price=discount_price,
            minimum_amount=minimum_amount,
            is_expired=is_expired
        )
        return redirect('coupon_list')  # Redirect to the coupon list after adding
    return render(request, 'customadmin/add_coupon.html')

def edit_coupon(request, pk):
    coupon = Coupon.objects.get(pk=pk)
    if request.method == 'POST':
        coupon.coupon_code = request.POST.get('coupon_code')
        coupon.discount_price = request.POST.get('discount_price')
        coupon.minimum_amount = request.POST.get('minimum_amount')
        coupon.is_expired = request.POST.get('is_expired') == 'on'
        coupon.save()  # Save the updated coupon

        return redirect('coupon_list')  # Redirect to the coupon list after editing
    return render(request, 'customadmin/edit_coupon.html', {'coupon': coupon})

@require_POST
def delete_coupon(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)

    # Handle the deletion
    coupon.delete()

    # Check if the request is AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    # Redirect to the coupon list if not an AJAX request
    return redirect('coupon_list')

# User module
@login_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'customadmin/user_list.html', {'users': users})

@login_required
def user_add(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username {username} is already taken.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, f'Email {email} is already registered.')
        else:
            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            messages.success(request, f'User {username} created successfully.')
            return redirect('user_list')  # Redirect to the user list or another appropriate view

    return render(request, 'customadmin/user_add.html')
@login_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.username = request.POST['username']
        user.email = request.POST['email']
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')

        password = request.POST.get('password')
        if password:
            user.set_password(password)

        user.save()
        messages.success(request, f'User {user.username} has been updated successfully.')
        return redirect('user_list')  # Redirect to the user list or another appropriate view

    return render(request, 'customadmin/user_edit.html', {'user': user})

@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('user_list')
    return render(request, 'customadmin/user_confirm_delete.html', {'user': user})


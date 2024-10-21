from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Wishlist,Review,SubCategory,Size
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_control, never_cache
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
from .forms import ReviewForm
from orders.models import Cart,CartItem
from django.db.models import Avg


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    if request.user.is_authenticated and not request.session.get('has_logged_in', False):
        messages.success(request, f'Welcome {request.user.username}!')
        request.session['has_logged_in'] = True
    featured_product = Product.objects.order_by('priority')[:4]
    latest_product = Product.objects.order_by('-id')[:4]
    context = {
        'featured_product': featured_product,
        'latest_product': latest_product
    }
    return render(request, 'index.html', context)

from django.shortcuts import render
from .models import Product

def list_of_product(request):
    query = request.GET.get('q', '')  # Get the search query from the request
    if query:
        # Filter products based on the search term
        products = Product.objects.filter(name__icontains=query)
    else:
        # If no search query, return all products
        products = Product.objects.all()

    # Return the product list template with the search results
    return render(request, 'shop.html', {'products': products})

def list_product(request):
    """
    Returns product list page with filtering options including size.
    """
    # Initialize the products QuerySet
    query = request.GET.get('q', '')  # Get the search query from the request
    if query:
        # Filter products based on the search term
        products = Product.objects.filter(name__icontains=query)
    else:
        # If no search query, return all products
        products = Product.objects.all()

    # Get category, subcategory, and size filters from the request
    category = request.GET.get('category')
    subcategory = request.GET.get('subcategory')
    size = request.GET.getlist('size')  # Get list of selected sizes

    # Filter by category
    if category:
        products = products.filter(category__name=category)

    # Filter by subcategory
    if subcategory:
        products = products.filter(sub_category__name=subcategory)

    # Filter by size (Many-to-Many relationship)
    if size:
        products = products.filter(sizes__name__in=size).distinct()

    # Filter by price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        try:
            min_price = float(min_price.replace('$', ''))
            max_price = float(max_price.replace('$', ''))
            products = products.filter(price__gte=min_price, price__lte=max_price)
        except (ValueError, InvalidOperation):
            pass

    # Pagination
    page = request.GET.get('page', 1)
    product_paginator = Paginator(products.order_by('priority'), 3)
    product_list = product_paginator.get_page(page)

    # Get all categories, subcategories, and available sizes for filtering options
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    sizes = Size.objects.all()  # Retrieve available sizes

    context = {
        'products': product_list,
        'min_price': min_price,
        'max_price': max_price,
        'category': category,
        'subcategory': subcategory,
        'categories': categories,
        'subcategories': subcategories,
        'sizes': sizes,
        'selected_sizes': size,
    }

    # if request.headers.get('x-requested-with') == 'XMLHttpRequest':
    #     return render(request, 'product_list.html', context)

    return render(request, 'shop.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
      # Get related products from the same subcategory, excluding the clicked product
    related_products = Product.objects.filter(sub_category=product.sub_category).exclude(id=product.id)
    for related_product in related_products:
        
        print("UBCATEGORY=====",related_product.price)

    sizes = Size.objects.all()  # Retrieve available sizes
    reviews = product.reviews.all().order_by('-created_at')  # Sort by date
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', pk=pk)
    else:
        form = ReviewForm()

    # Calculating average rating
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']  # Correct usage of Avg

    return render(request, 'product_details.html', {
        'product': product, 
        'reviews': reviews, 
        'form': form,
        'average_rating': average_rating,
        'sizes' : sizes
    })

def category_view(request, category_name):
    """
    Summary:
        Returns product list page

    Args:
        request (HttpRequest): The request object
        category_name (str): The name of the category to filter by

    Returns:
        HttpResponse: The rendered product list page
    """
    print("PPPPPP==",category_name)
    query = request.GET.get('q', '')  # Get the search query from the request
    if query:
        # Filter products based on the search term
        products = Product.objects.filter(category__name=category_name,name__icontains=query)
    else:
        # If no search query, return all products
        products = Product.objects.filter(category__name=category_name)
    print("produ==",products)
    # Initialize the products QuerySet


    # Get category, subcategory, and size filters from the request
    category = category_name
    subcategory = request.GET.get('subcategory')
    size = request.GET.getlist('size')  # Get list of selected sizes
    print("CATEGORY====",category)
    # Filter by category
    if category:
        products = products.filter(category__name=category)

    # Filter by subcategory
    if subcategory:
        products = products.filter(sub_category__name=subcategory)

    # Filter by size (Many-to-Many relationship)
    if size:
        products = products.filter(sizes__name__in=size).distinct()

    # Filter by price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        try:
            min_price = float(min_price.replace('$', ''))
            max_price = float(max_price.replace('$', ''))
            products = products.filter(price__gte=min_price, price__lte=max_price)
        except (ValueError, InvalidOperation):
            pass

    # Pagination
    page = request.GET.get('page', 1)
    product_paginator = Paginator(products.order_by('priority'), 3)
    product_list = product_paginator.get_page(page)

    # Get all categories, subcategories, and available sizes for filtering options
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    sizes = Size.objects.all()  # Retrieve available sizes

    context = {
        'products': product_list,
        'min_price': min_price,
        'max_price': max_price,
        'category': category,
        'subcategory': subcategory,
        'categories': categories,
        'subcategories': subcategories,
        'sizes': sizes,
        'selected_sizes': size,
    }

    # if request.headers.get('x-requested-with') == 'XMLHttpRequest':
    #     return render(request, 'product_list.html', context)

    return render(request, 'shop.html', context)


@login_required(login_url='/customer/login/')
def add_to_wishlist(request):
    if request.method == 'POST':
        user = request.user
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, pk=product_id)

        wishlist_item, created = Wishlist.objects.get_or_create(user=user, product=product)

        if created:
            message = 'Product added to wishlist successfully!'
            response_status = 200
        else:
            message = 'Product is already in your wishlist.'
            response_status = 400

        wishlist_count = Wishlist.objects.filter(user=user).count()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'message': message, 'wishlist_count': wishlist_count}, status=response_status)
        else:
            if response_status == 200:
                messages.success(request, message)
            else:
                messages.error(request, message)
            return redirect('product_detail', pk=product_id)

    return redirect('/customer/login_prompt/')

@login_required
def wishlist(request):
    user = request.user
    wishlist_items = Wishlist.objects.filter(user=user)
    wishlist_count = Wishlist.objects.filter(user=user).count()

    if not wishlist_items.exists():
        return render(request, 'wishlist_empty.html')
 
    if wishlist_count == 0:
        return redirect('wishlist_empty')  # Redirect to empty wishlist page

    context = {
        'wishlist_items': wishlist_items
    }
    return render(request, 'wishlist.html', context)

def wishlist_empty_view(request):
    return render(request, 'wishlist_empty.html')

def search(request):
    query = request.GET.get('query', '')  # Get the query from the URL parameters

    if query:
        results = Product.objects.filter(name__icontains=query)  # Search for products matching the query
    # else:
    #     results = Product.objects.all()  # If no query, return all products or handle it accordingly

    return render(request, 'search_results.html', {'results': results, 'query': query})

def remove_from_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        wishlist = Wishlist.objects.get(product=product_id)

        # Remove product from wishlist
        wishlist.delete()  
        return JsonResponse({'message': f'{product.name} has been removed from your wishlist!'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)

# def move_to_cart_ajax(request):
#     if request.method == 'POST':
#         product_id = request.POST.get('product_id')
#         product = get_object_or_404(Product, id=product_id)
#         wishlist, created = Wishlist.objects.get_or_create(user=request.user)
#         cart, created = Cart.objects.get_or_create(user=request.user)

#         # Remove from wishlist
#         if product in wishlist.products.all():
#             wishlist.products.remove(product)

#         # Add to cart
#         cart.products.add(product)

#         return JsonResponse({'message': f'{product.name} has been added to the cart!'}, status=200)

#     return JsonResponse({'error': 'Invalid request'}, status=400)

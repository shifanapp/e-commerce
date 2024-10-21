from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from . models import Profile
from orders.models import Order
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate,login ,logout 
from django.contrib import messages
from django.views.decorators.cache import cache_control,never_cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.hashers import check_password
from .models import Address
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.core.mail import EmailMessage


import logging

logger = logging.getLogger(__name__)

def register(request):
    errors = []
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone')
        agree_to_terms= request.POST.get('agree_to_terms')

        # Basic validation
        if not username:
            errors.append("Username is required.")
        if not email:
            errors.append("Email is required.")
        if not password1:
            errors.append("Password is required.")
        if not password2:
            errors.append("Password confirmation is required.")
        if not agree_to_terms:
            errors.append("You must agree to the terms and conditions.")

        # If no errors so far, proceed with further validation
        if not errors:
            if password1 != password2:
                errors.append("Passwords do not match.")
            if User.objects.filter(username=username).exists():
                errors.append("Username already exists.")
            if User.objects.filter(email=email).exists():
                errors.append("Email already exists.")
            
            # Create user account if no errors
            if not errors:
                user = User.objects.create(
                    username=username,
                    email=email,
                    password=make_password(password1)
                )
                customer = Profile.objects.create(
                    user=user,
                    phone=phone,
                )
                user.is_active = False  # Deactivate account until email confirmation
                user.save()

                # Send verification email
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                current_site = get_current_site(request)
                subject = 'Activate your account'
                message = render_to_string('activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': uid,
                    'token': token,
                })
                plain_message = f"Hi {user.username},\nPlease click the following link to confirm your email address and complete your registration:\nhttp://{current_site.domain}{reverse('activate', kwargs={'uidb64': uid, 'token': token})}"

                email = EmailMultiAlternatives(
                    subject, plain_message, 'shifanashif30@gmail.com', [email]
                )
                email.attach_alternative(message, "text/html")
                
                try:
                    email.send()
                    messages.success(request, 'Please confirm your email address to complete the registration.')
                    return redirect('register')  # Redirect to the same page to show the success message
                except Exception as e:
                    logger.error(f"Error sending email: {e}")
                    errors.append(f"Error sending email: {e}")
                    messages.error(request, f"Error sending email: {e}")

    if errors:
        for error in errors:
            messages.error(request, error)

    return render(request, 'register.html')
@never_cache
def login_view(request):
    user=None
    if request.method=='POST':
            username=request.POST.get('username')
            password=request.POST.get('password')
            user=authenticate(request,username=username,password=password)   
            print(username)
            if user :
                
                print(password)

                login(request,user)
                return redirect('home')
            else:
                messages.error(request,'Invalid username and password')
    return render(request,'login.html')
 
def logout_view(request):
    request.session['has_logged_in'] = False
    logout(request)
    return redirect('home')

def my_account(request):
    user=request.user
    customer = request.user.customer_profile
    addresses = Address.objects.filter(user=request.user)

    all_orders = Order.objects.filter(owner=customer)
    users=Profile.objects.get(user=user)
    print("USERS=====",users.last_name)
    return render(request, 'my_account.html', {'addresses':addresses,'user':user,'orders':all_orders,'users':users})
@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        print(current_password)
        print(new_password)
        print(confirm_password)
        if not check_password(current_password, request.user.password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Important to keep the user logged in after password change
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('my_account')  # Redirect to a page of your choice

    return render(request, 'my_account.html')
def forgot_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password != confirm_new_password:
            messages.error(request, 'New passwords do not match.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Keeps the user logged in
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('home')

    return render(request, 'forgot_password.html')

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            current_site = get_current_site(request)
            subject = 'Reset Your Password'
            # Render the HTML template as a string
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http',
            })
            # Create an email message with the rendered HTML content
            email_message = EmailMessage(
                subject,
                message,
                'from@example.com',  # Replace with your 'from' email address
                [user.email],
            )
            email_message.content_subtype = 'html'  # Set the content subtype to HTML
            email_message.send()
            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('password_reset_done')
        except User.DoesNotExist:
            messages.error(request, 'No user found with that email address.')
    
    return render(request, 'password_reset_form.html')

def password_reset_confirm(request, uidb64, token):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        if new_password != confirm_new_password:
            messages.error(request, 'New passwords do not match.')
        else:
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
                if default_token_generator.check_token(user, token):
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Your password has been reset successfully.')
                    return redirect('password_reset_complete')
                else:
                    messages.error(request, 'Password reset link is invalid.')
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                messages.error(request, 'Password reset link is invalid.')

    return render(request, 'password_reset_confirm.html')

def password_reset_done(request):
    return render(request, 'password_reset_done.html')

def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')


@login_required
def list_addresses(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'list_addresses.html', {'addresses': addresses})

import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)

@login_required
def manage_addresses(request):
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

            elif action == 'edit' and address_id:
                print("EDIT=====")
                address = Address.objects.get(id=address_id, user=request.user)
                address.line1 = line1
                address.line2 = line2
                address.city = city
                address.state = state
                address.country = country
                address.zip_code = zip_code
                address.phone_number = phone_number
                address.is_default = is_default
                address.save()
                
                address_data = {
                    'id': address.id,
                    'line1': address.line1,
                    'line2': address.line2,
                    'city': address.city,
                    'state': address.state,
                    'country': address.country,
                    'zip_code': address.zip_code,
                    'phone_number': address.phone_number,
                    'is_default': address.is_default,
                }
                print(address_data)
                return JsonResponse({'message': 'Address updated successfully!', 'address': address_data})

            elif action == 'delete' and address_id:
                address = get_object_or_404(Address, id=address_id, user=request.user)
                address.delete()
                return JsonResponse({'message': 'Address deleted successfully!', 'address_id': address_id})

        except Exception as e:
            logger.error(f"Error processing form: {e}")
            return JsonResponse({'error': str(e)}, status=400)

    addresses = Address.objects.filter(user=request.user)
    return render(request, 'my_account.html', {'addresses': addresses})

def login_prompt_view(request):
    # logout(request)
    return render (request,'login_prompt.html')



def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Thank you for your email confirmation. You can now login to your account.')
    else:
        return HttpResponse('Activation link is invalid!')
    
@login_required
def update_account(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')

        # Validate the mobile number
        if not mobile.isdigit() or len(mobile) != 10:
            return JsonResponse({'success': False, 'message': 'Invalid phone number.'})

        # Update the current user
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        # Update the profile
        profile = user.customer_profile
        profile.first_name = first_name
        profile.last_name = last_name
        profile.phone = mobile
        profile.email = email
        profile.save()

        return JsonResponse({'success': True, 'message': 'Account updated successfully!'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

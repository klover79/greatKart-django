from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from orders.models import Order,OrderProduct
from carts.models import Cart, CartItem
from carts.views import _cart_id
from django.contrib.auth.hashers import make_password
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
import requests

# verification send email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name      = form.cleaned_data['first_name']
            last_name       = form.cleaned_data['last_name']
            phone_number    = form.cleaned_data['phone_number']
            email           = form.cleaned_data['email']
            password        = form.cleaned_data['password']
            username        = email.split("@")[0]

            user = Account.objects.create(first_name=first_name,
                                          last_name=last_name,                                          
                                          email=email,
                                          username=username,
                                          password=make_password(password))
            user.phone_number = phone_number
            user.save()

            # create user profile
            profile = UserProfile()
            profile.user_id = user.id #TODO check if user id exist, delete the user id profile before save
            profile.profile_picture = 'default/default-user.png'
            profile.save()




            # user activation
            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            # messages.success(request, 'We have received your registration. Please verify you email address by clicking on the link that we have sent you.')
            return redirect('/accounts/login/?command=verification&email='+ email)
    else: #render the empty   
        form = RegistrationForm()
    context = {
            'form':form,
        }

    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email,password=password)
        if user is not None:

            # checking if cart items exists before login
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    product_variation =[]
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation  = item.variations.all()
                        ex_var_list.append(list(existing_variation)) 
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()

            except:
                pass

            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                print(url)
                query = requests.utils.urlparse(url).query
                print('query -->', query)
                params = dict(x.split('=') for  x in query.split('&'))
                print('query -->', query)
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage) 
            except:
                return redirect('accounts:dashboard')
            
        else:
            messages.error(request,'Invalid login credentials')
            return redirect('accounts:login')
    return render(request, 'accounts/login.html')

@login_required(login_url = 'accounts:login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('accounts:login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except(TypeError,ValueError,OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your account is activated.")
        return redirect('accounts:login')
    else:
        messages.error(request, "Invalid registration link")
        return redirect('accounts:register')
    
@login_required(login_url='accounts:login')
def dashboard(request):
    orders       = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    user_profile = UserProfile.objects.get(user_id = request.user.id)

    context = {
        'orders_count': orders_count,
        'user_profile'  : user_profile,
    }

    return render(request, 'accounts/dashboard.html', context)

def reset_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        user_exist = Account.objects.filter(email__exact=email).exists()
        if user_exist:
            user = Account.objects.get(email=email)
            # user reset password
            current_site = get_current_site(request)
            mail_subject = "Reset your passoword"
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request, 'Password reset email has been sent to your email: ' + email)
            return redirect('accounts:login')
        else:
            messages.error(request, 'No user associated with the email provided!')
            return redirect('accounts:reset-password')

    return render(request, 'accounts/reset_password.html')
     
    
def reset_password_validate(request,uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except(TypeError,ValueError,OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request, "Please reset your password.")
        return redirect('accounts:reset-password-detail')
    else:
        messages.error(request, "Invalid password reset link or link has expired!")
        return redirect('accounts:password-reset')
    

def reset_password_detail(request):
    if request.method == 'POST':
        password            = request.POST['password']
        confirm_password    = request.POST['confirm_password']
        if password == confirm_password:
            user = Account.objects.get(pk=request.session.get('uid'))
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset was succesful')
            return redirect('accounts:login')

        else:
            messages.error(request, 'Password did not match!')
            return redirect('accounts:reset-password-detail')
    else:
        return render(request, 'accounts/reset_password_detail.html')
    
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)

def edit_profile(request):
    
    userprofile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        user_form       = UserForm(request.POST, instance=request.user)
        profile_form    = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts:edit-profile')
    else:
        user_form       = UserForm(instance=request.user)
        profile_form    = UserProfileForm(instance=userprofile)

    context = {
        'user_form'     : user_form,
        'profile_form'  : profile_form,
        'userprofile'   : userprofile,
    }


    return render(request, 'accounts/edit_profile.html', context)

@login_required(login_url='accounts:login')
def change_password(request):
    if request.method == 'POST':
        current_password    = request.POST['current_password']
        new_password        = request.POST['new_password']
        confirm_password    = request.POST['confirm_password']

        user = Account.objects.get(username__exact = request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password updated successfully')
                return redirect('accounts:dashboard')
            else:
                messages.error(request, 'Current password is invalid!')
                return redirect('accounts:change-password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('accounts:change-password')
    else:    

        return render(request, 'accounts/change_password.html' )
    
@login_required(login_url='accounts:login')
def order_detail(request, order_id):

    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)

    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity


    context = {
        'order_detail'  : order_detail,
        'order'         : order,
        'subtotal'      : subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)
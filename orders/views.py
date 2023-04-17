from django.shortcuts import render, redirect
from django.http import JsonResponse
from carts.models import CartItem
from .forms import OrderForm
from orders.models import Order, Payment, OrderProduct
from store.models import Product
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import datetime
import json


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    # store transaction details inside payments

    payment = Payment(
        user            = request.user,
        payment_id      = body['transID'],
        payment_method  = body['payment_method'],
        amount_paid     = order.order_total,
        status          = body['status']
    )
    payment.save()

    order.payment       = payment
    order.is_ordered    = True
    order.save()

    # move cart item to order product table 
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        order_product               = OrderProduct()
        order_product.order_id      = order.id 
        order_product.payment       = payment
        order_product.user_id       = request.user.id
        order_product.product_id    = item.product.id
        order_product.quantity      = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered       = True
        order_product.save()

        cart_item           = CartItem.objects.get(id=item.id)
        product_variation   = cart_item.variations.all()
        order_product       = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variation)
        order_product.save()



        # reduct the quantity of sold product
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # clear the cart item
    CartItem.objects.filter(user=request.user).delete()

    # send email to the customer
    mail_subject = "Thank you for your purchase!"
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject,message,to=[to_email])
    send_email.send()

    # send back the transation id to the paypal
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)

def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items    =  CartItem.objects.filter(user=current_user)

    if cart_items.count() <= 0:
        return redirect('stores:store')
    
    grand_total  = 0
    tax          = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = round(total * 0.02,2) # times tax percentage parameter
    grand_total = round((tax + total),2)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # store information in the order table
            data = Order()
            data.user           = current_user
            data.first_name     = form.cleaned_data['first_name']
            data.last_name      = form.cleaned_data['last_name']
            data.phone_number   = form.cleaned_data['phone_number']
            data.email          = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country        = form.cleaned_data['country']
            data.state          = form.cleaned_data['state']
            data.city           = form.cleaned_data['city']
            data.order_note     = form.cleaned_data['order_note']
            data.order_total    = grand_total
            data.tax            = tax
            data.ip             = request.META.get('REMOTE_ADDR')
            data.save()
            # generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d  = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number   = order_number
            data.save()

            order = Order.objects.get(user=current_user,is_ordered=False, order_number=order_number) 
            context = {
                'order'      :order,
                'cart_items' : cart_items,
                'tax'        : tax,
                'total'      : total,
                'grand_total': grand_total,
            }

            return render(request, 'orders/payments.html', context)
    else:
        return redirect('carts:checkout')
        

def order_completed(request):
    context = None
    return render(request, 'orders/order_completed.html', context)
    


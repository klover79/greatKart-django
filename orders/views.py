from django.shortcuts import render, redirect
from carts.models import CartItem
from .forms import OrderForm
from orders.models import Order, Payment
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

    order.payment = payment
    order.is_ordered = True
    order.save()

    print(body)
    return render(request, 'orders/payments.html' )

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
        

 

    


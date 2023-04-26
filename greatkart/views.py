from django.shortcuts import render
from store.models import Product
from orders.models import ReviewRating

def home(request):
    products = Product.objects.filter(is_available=True).order_by('create_date')
    # get rating
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products'  : products,
        'reviews'   : reviews,
    }
    return render(request, 'home.html', context)
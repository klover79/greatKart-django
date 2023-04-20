from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category
from orders.models import ReviewRating, OrderProduct
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages




def store(request, category_slug=None):
    categories = None
    products = None
    item_per_page = 4 #TODO: in parameter model, set page number for stores

    if category_slug!=None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('id')
        paginator = Paginator(products, item_per_page)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
    else:
        products = Product.objects.filter(is_available=True)
        paginator = Paginator(products, item_per_page)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

    context = {
        'products': paged_products
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product  = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    
    try:
        if request.user:
            order_product = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        else:
            order_product = None 
    except (OrderProduct.DoesNotExist,TypeError):
        order_product = None 

    
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    
    context = {
        'single_product': single_product,
        'in_cart'       : in_cart,
        'order_product' : order_product,
        'reviews'       : reviews,
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    item_per_page = 3
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-create_date').filter(Q(description__icontains=keyword)| 
                                                                       Q(product_name__icontains=keyword))
            
        else:
            products = Product.objects.filter(is_available=True)
           
        context = {          
        'products':products
                    }
    
    return render(request,'store/store.html', context)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you. Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject    = form.cleaned_data['subject']
                data.rating     = form.cleaned_data['rating']
                data.review     = form.cleaned_data['review']
                data.ip         = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id    = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted' )
                return redirect(url) 
    
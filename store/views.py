from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q


def store(request, category_slug=None):
    categories = None
    products = None
    item_per_page = 3 #TODO: in parameter model, set page number for stores

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

    context = {
        'single_product': single_product,
        'in_cart'       : in_cart,
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
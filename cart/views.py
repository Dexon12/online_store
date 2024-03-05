from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST

from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from coupons.forms import CouponApplyForm
from shop.recommender import Recommender

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id) 
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'], override_quantity=cd['override'])
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail') # Почему используется редирект

def cart_detail(request):
    cart = Cart(request)
    for item in cart: # Когда проходимся по корзине вызывается метод __iter__, который переопределен и выдает информацию. Корзина и товары храняться в сессии, это определяется в __init__ классе корзины
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })             # обновляется форма с предварительно заполненными данными
    coupon_apply_form = CouponApplyForm()   

    r = Recommender()
    cart_products = [item['product'] for item in cart] # список продуктов в корзине
    if(cart_products): # Есть ли тут продукты 
        recommended_products = r.suggest_products_for(
            cart_products,
            max_results=4
        ) # Товары для рекомендации, максимум 4
    else:
        recommended_products = []

    return render(request, 'cart/detail.html', {'cart': cart, 'coupon_apply_form': coupon_apply_form, 'recommended_products': recommended_products})

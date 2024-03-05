from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Coupon
from .forms import CouponApplyForm  

@require_POST
def coupon_apply(request):
    now = timezone.now()
    form = CouponApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code,valid_from__lte=now, valid_to__gte=now, active=True) # What is __iexact (учитывается регистрозависимость), __lte (значение поля меньше или равно указанному значению) __gte (значение поля больше или равно указанному значению)?
            request.session['coupon_id'] = coupon.id # получаем id купона из сессии 
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
    return redirect('cart:cart_detail')
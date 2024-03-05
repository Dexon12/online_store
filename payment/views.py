from decimal import Decimal
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, reverse,\
                             get_object_or_404
from orders.models import Order


# create the Stripe instance
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def payment_process(request):
    order_id = request.session.get('order_id', None)
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(
                        reverse('payment:completed')) # What is build_absolut_uri? What a different between reverse and reverselazy(Все тоже самое как и с другими ленивыми функциями, они выполняются не сразу, а только когда надо) Сюда перекидывает после оплаты
        cancel_url = request.build_absolute_uri( # Тут строиться абсолютный url адрес для представления payment_canceled
                        reverse('payment:canceled')) # Сюда перекидывает в случе отказа

        # Stripe checkout session data
        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }
        # add order items to the Stripe checkout session
        for item in order.items.all():
            session_data['line_items'].append({ # What is line_items? в контексте Stripe Checkout Session представляет собой список товаров или элементов, которые пользователь покупает в рамках этой сессии оплаты. Каждый элемент списка представляет отдельный товар в корзине.
                'price_data': { # Информация о цене товара.
                    'unit_amount': int(item.price * Decimal('100')), # Сумма в центах (в данном случае, цена товара, умноженная на 100 и преобразованная в целое число).
                    'currency': 'usd', # Валюта (в данном случае, доллары США).
                    'product_data': { # Информация о товаре.
                        'name': item.product.name, # Название товара (в данном случае, item.product.name).
                    },
                },
                'quantity': item.quantity, # Количество единиц товара в заказе (item.quantity).
            })

        # Stripe coupon
        if order.coupon:
            stripe_coupon = stripe.Coupon.create(
                                name=order.coupon.code,
                                percent_off=order.discount,
                                duration='once')
            session_data['discounts'] = [{
                'coupon': stripe_coupon.id
            }]

        # create Stripe checkout session
        session = stripe.checkout.Session.create(**session_data)

        # redirect to Stripe payment form
        return redirect(session.url, code=303) # Why we give code=303?Код 303 указывает браузеру использовать метод GET при следующем запросе.

    else:
        return render(request, 'payment/process.html', locals())


def payment_completed(request): # In what event does it happend? Когда происходит успешная оплата 
    return render(request, 'payment/completed.html')


def payment_canceled(request): # In what event does it happend? Когда оплата не проходит
    return render(request, 'payment/canceled.html')
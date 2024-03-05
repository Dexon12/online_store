import stripe

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from orders.models import Order

"""
Страйп понимает когда отправлять вебхук, потому что во вью оплаты мы создает страйп чекаут и передаем туда список с данными
Ваш вебхук принимает этот запрос, проверяет его подлинность, обрабатывает данные события и выполняет необходимые действия, например, обновляет статус заказа в вашей системе.
Таким образом, вебхуки обеспечивают асинхронное уведомление между сервисами о важных событиях, что позволяет им взаимодействовать в реальном времени
"""
@csrf_exempt # external services doesn't require/know about the CSRF 
def stripe_webhook(request): 
    payload = request.body # HTTP -> method, version (request line) | headers | message body Получает данные вебхука из тела HTTP-запроса
    sig_header = request.META['HTTP_STRIPE_SIGNATURE'] # verify if the event is genuinely from Stripe API  Получает подпись вебхука из заголовка HTTP.
    event = None # initialize None, will hold event 

    try: # Проверка подписи вебхука 
        event = stripe.Webhook.construct_event( # Используется библиотека Stripe для проверки подписи вебхука. stripe.Webhook.construct_event проверяет подлинность события, используя данные запроса, подпись и секретный ключ вебхука. Если проверка неудачна, возвращается HTTP-ответ с кодом 400.
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e: # potentially tampered
        return HttpResponse(status=400)
    
    if event.type == 'checkout.session.completed': # if it's successful, refers to the documentations 
        session = event.data.object # Проверяется тип события, и если это checkout.session.completed, то извлекается объект сессии из данных события.
        if session.mode == 'payment' and session.payment_status == 'paid': # if that's paid
            try:
                order = Order.objects.get(id=session.client_reference_id) # Получается соответствующий заказ по client_reference_id из данных сессии.
            except Order.DoesNotExist:
                return HttpResponse(status=404) 
            order.paid = True
            order.stripe_id = session.payment_intent
            
            order.save()

    return HttpResponse(status=200)

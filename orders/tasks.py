from celery import shared_task
from django.core.mail import send_mail
from .models import Order


@shared_task # Декоратор @shared_task в Django используется для создания задач, которые могут быть выполнены асинхронно
def order_created(order_id):
    """
    Task to send an e-mail notification when an order is
    successfully created.
    """
    order = Order.objects.get(id=order_id)
    subject = f'Order nr. {order.id}'
    message = f'Dear {order.first_name},\n\n' \
              f'You have successfully placed an order.' \
              f'Your order ID is {order.id}.'
    mail_sent = send_mail(subject,
                          message,
                          'admin@myshop.com',
                          [order.email])
    return mail_sent

# Примерный порядок действий:

# В вашем коде, когда заказ успешно создан, вы вызываете order_created.delay(order.id).
# Эта задача (order_created) добавляется в очередь.
# Ваша основная программа может продолжить выполнение без ожидания завершения задачи.
# Система очередей, такая как Celery, обрабатывает задачу асинхронно, не блокируя основной поток выполнения.
# Когда задача будет обработана, выполнится код внутри order_created, который извлечет заказ из базы данных, сформирует сообщение и отправит уведомление по электронной почте.
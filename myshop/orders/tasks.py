from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from .models import Order


@shared_task
def order_created(order_id):
    """
    Отправка уведомления по электронной почте при создании заказа.
    """
    order = Order.objects.get(id=order_id)
    subject = f'Order No. {order_id}'
    message = (
        f'Dear {order.first_name},\n\n'
        f'You have sucessfully placed an order.'
        f'Your order number is {order_id}.'
    )
    mail_sent = send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[order.email, ]
    )
    return mail_sent

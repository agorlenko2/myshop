from decimal import Decimal

from django.shortcuts import (
    render, redirect, get_object_or_404
)
from django.urls import reverse
from django.conf import settings
import stripe

from orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def payment_process(request):
    order_id = request.session.get('order_id', None)
    order = get_object_or_404(
        Order,
        id=order_id
    )
    if request.method == 'POST':
        success_url = request.build_absolute_uri(
            reverse('payment:completed')
        )
        cancel_url = request.build_absolute_uri(
            reverse('payment:cancelled')
        )
        session_data = {
            'mode': 'payment',
            'client_reference_id': order_id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }
        for item in order.items.all():
            session_data['line_items'].append(
                {
                    'price_data': {
                        # Unit amount has to be counted in cents
                        'unit_amount': int(item.price * Decimal('100')),
                        'currency': 'usd',
                        'product_data': {
                            'name': item.product.name,
                        }
                    },
                    'quantity': item.quantity
                }
            )
        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)
    else:
        return render(
            request=request,
            template_name='payment/process.html',
            context=locals()
        )


def payment_completed(request):
    return render(request=request, template_name='payment/completed.html')


def payment_cancelled(request):
    return render(request=request, template_name='payment/cancelled.html')

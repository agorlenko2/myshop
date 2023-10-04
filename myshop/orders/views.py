from django.shortcuts import (
    render, redirect, get_object_or_404
)
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint

from cart.cart import Cart
from .forms import OrderCreateForm
from .models import OrderItem, Order
from .tasks import order_created


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            cart.clear()
            order_created.delay(order.id)
            # return render(
            #     request=request,
            #     template_name='orders/order/created.html',
            #     context={
            #         'order': order,
            #     }
            # )
            request.session['order_id'] = order.id
            return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()
    return render(
        request=request,
        template_name='orders/order/create.html',
        context={
            'cart': cart,
            'form': form
        }
    )


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(
        request=request,
        template_name='admin/orders/order/detail.html',
        context={
            'order': order
        }
    )


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string(
        template_name='orders/order/pdf.html',
        context={
            'order': order
        }
    )
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    weasyprint.HTML(string=html).write_pdf(
        target=response,
        stylesheets=[
            weasyprint.CSS(
                settings.STATIC_ROOT / 'css/pdf.css'
            )
        ]
    )
    return response

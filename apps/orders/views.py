"""
ویوهای اپ orders
"""
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.db import transaction

from .models import Order, OrderItem, PaymentTransaction, ShippingMethod
from apps.cart.models import Cart, CouponUsage
from apps.accounts.models import Address
from .zarinpal import ZarinPalService

logger = logging.getLogger(__name__)


class CheckoutView(LoginRequiredMixin, View):
    """صفحه تسویه حساب"""
    
    template_name = 'orders/checkout.html'
    
    def get(self, request):
        # دریافت سبد خرید
        cart = Cart.objects.filter(user=request.user).first()
        
        if not cart or cart.items_count == 0:
            messages.warning(request, 'سبد خرید شما خالی است')
            return redirect('cart:cart')
        
        # بررسی موجودی
        for item in cart.items.select_related('product').all():
            if not item.is_available:
                messages.error(
                    request,
                    f'محصول {item.product.name} موجود نیست یا موجودی کافی ندارد'
                )
                return redirect('cart:cart')
        
        # آدرس‌های کاربر
        addresses = request.user.addresses.all()
        
        # روش‌های ارسال
        shipping_methods = ShippingMethod.objects.filter(is_active=True)
        
        context = {
            'cart': cart,
            'addresses': addresses,
            'shipping_methods': shipping_methods,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        
        if not cart or cart.items_count == 0:
            messages.warning(request, 'سبد خرید شما خالی است')
            return redirect('cart:cart')
        
        # دریافت آدرس
        address_id = request.POST.get('address_id')
        
        if address_id:
            # انتخاب آدرس موجود
            address = get_object_or_404(Address, pk=address_id, user=request.user)
        else:
            # ایجاد آدرس جدید از فرم
            title = request.POST.get('new_address_title', '').strip()
            province = request.POST.get('new_address_province', '').strip()
            city = request.POST.get('new_address_city', '').strip()
            full_address = request.POST.get('new_address_full', '').strip()
            postal_code = request.POST.get('new_address_postal_code', '').strip()
            receiver_name = request.POST.get('new_address_receiver_name', '').strip()
            receiver_phone = request.POST.get('new_address_receiver_phone', '').strip()
            
            # اعتبارسنجی
            if not all([province, city, full_address, postal_code, receiver_name, receiver_phone]):
                messages.error(request, 'لطفاً تمام فیلدهای آدرس را پر کنید')
                return redirect('orders:checkout')
            
            # ایجاد آدرس جدید
            is_first_address = not request.user.addresses.exists()
            address = Address.objects.create(
                user=request.user,
                title=title or 'آدرس من',
                province=province,
                city=city,
                address=full_address,
                postal_code=postal_code,
                receiver_name=receiver_name,
                receiver_phone=receiver_phone,
                is_default=is_first_address  # اولین آدرس به عنوان پیش‌فرض
            )
        
        # دریافت روش ارسال
        shipping_id = request.POST.get('shipping_id')
        shipping = None
        shipping_cost = 0
        shipping_method_name = ''
        
        if shipping_id:
            shipping = get_object_or_404(ShippingMethod, pk=shipping_id, is_active=True)
            shipping_cost = shipping.price
            shipping_method_name = shipping.name
        
        # یادداشت
        note = request.POST.get('note', '')
        
        # ایجاد سفارش
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                address_title=address.title,
                address_province=address.province,
                address_city=address.city,
                address_full=address.address,
                address_postal_code=address.postal_code,
                receiver_name=address.receiver_name,
                receiver_phone=address.receiver_phone,
                subtotal=cart.subtotal,
                shipping_cost=shipping_cost,
                discount_amount=cart.discount_amount,
                coupon_code=cart.coupon.code if cart.coupon else '',
                total=cart.total + shipping_cost,
                shipping_method=shipping_method_name,
                note=note,
            )
            
            # ایجاد آیتم‌های سفارش
            for item in cart.items.select_related('product').all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                    product_name=item.product.name,
                    product_sku=item.product.sku,
                )
            
            # ثبت استفاده از کوپن
            if cart.coupon:
                CouponUsage.objects.create(
                    coupon=cart.coupon,
                    user=request.user,
                    order=order,
                    discount_amount=cart.discount_amount
                )
                cart.coupon.used_count += 1
                cart.coupon.save()
        
        # ذخیره شناسه سفارش در session
        request.session['pending_order_id'] = order.pk
        
        return redirect('orders:payment', pk=order.pk)


class PaymentView(LoginRequiredMixin, View):
    """صفحه پرداخت"""
    
    template_name = 'orders/payment.html'
    
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        
        if order.status != 'pending':
            messages.warning(request, 'این سفارش قبلاً پردازش شده است')
            return redirect('dashboard:order_detail', pk=order.pk)
        
        context = {
            'order': order,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        
        logger.info(f"Payment POST request for order {order.order_number} by user {request.user}")
        
        if order.status != 'pending':
            messages.error(request, 'این سفارش قبلاً پردازش شده است')
            return redirect('dashboard:order_detail', pk=order.pk)
        
        # ایجاد تراکنش پرداخت
        transaction_obj = PaymentTransaction.objects.create(
            order=order,
            amount=order.total,
            gateway='zarinpal',
        )
        
        logger.info(f"Created PaymentTransaction {transaction_obj.pk} for order {order.order_number}")
        
        # ایجاد درخواست پرداخت
        callback_url = request.build_absolute_uri(
            reverse('orders:payment_callback')
        )
        
        logger.info(f"Callback URL: {callback_url}")
        
        result = ZarinPalService.create_payment(order, callback_url)
        
        logger.info(f"ZarinPal create_payment result: {result}")
        
        if result['success']:
            transaction_obj.authority = result['authority']
            transaction_obj.save()
            
            logger.info(f"Redirecting to payment gateway: {result['payment_url']}")
            return redirect(result['payment_url'])
        else:
            transaction_obj.status = 'failed'
            transaction_obj.save()
            
            error_msg = result.get('message', 'خطا در اتصال به درگاه پرداخت')
            logger.error(f"Payment failed for order {order.order_number}: {error_msg}")
            messages.error(request, error_msg)
            return redirect('orders:payment', pk=order.pk)


class PaymentCallbackView(LoginRequiredMixin, View):
    """کالبک پرداخت"""
    
    def get(self, request):
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')
        
        if not authority:
            messages.error(request, 'پارامترهای نامعتبر')
            return redirect('dashboard:orders')
        
        # یافتن تراکنش
        try:
            payment = PaymentTransaction.objects.get(authority=authority)
        except PaymentTransaction.DoesNotExist:
            messages.error(request, 'تراکنش یافت نشد')
            return redirect('dashboard:orders')
        
        order = payment.order
        
        if status != 'OK':
            payment.status = 'canceled'
            payment.save()
            
            messages.warning(request, 'پرداخت لغو شد')
            return redirect('orders:payment_failed', pk=order.pk)
        
        # تایید پرداخت
        result = ZarinPalService.verify_payment(authority, order.total)
        
        if result['success']:
            with transaction.atomic():
                # بروزرسانی تراکنش
                payment.status = 'success'
                payment.ref_id = result['ref_id']
                payment.card_number = result.get('card_pan', '')
                payment.save()
                
                # بروزرسانی سفارش
                order.status = 'paid'
                order.paid_at = timezone.now()
                order.save()
                
                # کاهش موجودی
                for item in order.items.select_related('product').all():
                    product = item.product
                    product.stock_quantity -= item.quantity
                    product.sales_count += item.quantity
                    product.save()
                
                # خالی کردن سبد خرید
                Cart.objects.filter(user=request.user).delete()
            
            messages.success(request, 'پرداخت با موفقیت انجام شد')
            return redirect('orders:payment_success', pk=order.pk)
        else:
            payment.status = 'failed'
            payment.save()
            
            messages.error(
                request,
                result.get('message', 'تایید پرداخت ناموفق بود')
            )
            return redirect('orders:payment_failed', pk=order.pk)


class PaymentSuccessView(LoginRequiredMixin, View):
    """صفحه موفقیت پرداخت"""
    
    template_name = 'orders/payment_success.html'
    
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        
        context = {
            'order': order,
        }
        
        return render(request, self.template_name, context)


class PaymentFailedView(LoginRequiredMixin, View):
    """صفحه عدم موفقیت پرداخت"""
    
    template_name = 'orders/payment_failed.html'
    
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        
        context = {
            'order': order,
        }
        
        return render(request, self.template_name, context)


class CancelOrderView(LoginRequiredMixin, View):
    """لغو سفارش"""
    
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        
        if order.cancel():
            messages.success(request, 'سفارش با موفقیت لغو شد')
        else:
            messages.error(request, 'امکان لغو این سفارش وجود ندارد')
        
        return redirect('dashboard:order_detail', pk=order.pk)

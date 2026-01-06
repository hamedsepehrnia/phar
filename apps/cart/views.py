"""
ویوهای اپ cart
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from .models import Cart, CartItem, Coupon
from apps.catalog.models import Product


class CartMixin:
    """میکسین برای دسترسی به سبد خرید"""
    
    def get_cart(self, request):
        """دریافت یا ایجاد سبد خرید"""
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            # ادغام سبد مهمان با سبد کاربر
            session_key = request.session.session_key
            if session_key:
                try:
                    guest_cart = Cart.objects.get(
                        session_key=session_key,
                        user__isnull=True
                    )
                    # انتقال آیتم‌ها
                    for item in guest_cart.items.all():
                        cart.add_item(item.product, item.quantity)
                    guest_cart.delete()
                except Cart.DoesNotExist:
                    pass
        else:
            if not request.session.session_key:
                request.session.create()
            
            session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        
        return cart


class CartView(CartMixin, View):
    """نمایش سبد خرید"""
    
    # TEMP: تست سرعت - برای برگشت به حالت اصلی این خط رو کامنت بزنید و خط بعدی رو آنکامنت کنید
    template_name = 'cart/cart_minimal.html'
    # template_name = 'cart/cart_detail.html'
    
    def get(self, request):
        cart = self.get_cart(request)
        
        # بررسی موجودی آیتم‌ها
        unavailable_items = []
        for item in cart.items.select_related('product').all():
            if not item.is_available:
                unavailable_items.append(item)
        
        context = {
            'cart': cart,
            'unavailable_items': unavailable_items,
        }
        
        return render(request, self.template_name, context)


class AddToCartView(CartMixin, View):
    """افزودن به سبد خرید"""
    
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        quantity = int(request.POST.get('quantity', 1))
        
        # بررسی موجودی
        if not product.is_in_stock:
            message = 'این محصول موجود نیست'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': message})
            messages.error(request, message)
            return redirect(request.META.get('HTTP_REFERER', 'cart:detail'))
        
        # بررسی حداکثر تعداد
        max_qty = min(product.stock_quantity, product.max_purchase_per_user)
        if quantity > max_qty:
            quantity = max_qty
        
        cart = self.get_cart(request)
        cart.add_item(product, quantity)
        
        message = f'{product.name} به سبد خرید اضافه شد'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': message,
                'cart_count': cart.items_count,
                'cart_total': str(cart.total)
            })
        
        messages.success(request, message)
        return redirect(request.META.get('HTTP_REFERER', 'cart:detail'))


class RemoveFromCartView(CartMixin, View):
    """حذف از سبد خرید"""
    
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        cart = self.get_cart(request)
        cart.remove_item(product)
        
        message = f'{product.name} از سبد خرید حذف شد'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': message,
                'cart_count': cart.items_count,
                'cart_total': str(cart.total)
            })
        
        messages.success(request, message)
        return redirect('cart:detail')


class UpdateCartItemView(CartMixin, View):
    """بروزرسانی تعداد آیتم سبد"""
    
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        cart = self.get_cart(request)
        cart.update_item_quantity(product, quantity)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # محاسبه مجدد قیمت آیتم
            item_total = product.price * quantity if quantity > 0 else 0
            
            return JsonResponse({
                'success': True,
                'item_total': str(item_total),
                'cart_count': cart.items_count,
                'cart_subtotal': str(cart.subtotal),
                'cart_discount': str(cart.discount_amount),
                'cart_total': str(cart.total)
            })
        
        return redirect('cart:detail')


class ClearCartView(CartMixin, View):
    """خالی کردن سبد خرید"""
    
    def post(self, request):
        cart = self.get_cart(request)
        cart.clear()
        
        message = 'سبد خرید خالی شد'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': message
            })
        
        messages.success(request, message)
        return redirect('cart:detail')


class ApplyCouponView(CartMixin, View):
    """اعمال کد تخفیف"""
    
    def post(self, request):
        code = request.POST.get('code', '').strip().upper()
        
        if not code:
            message = 'لطفاً کد تخفیف را وارد کنید'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': message})
            messages.error(request, message)
            return redirect('cart:detail')
        
        cart = self.get_cart(request)
        user = request.user if request.user.is_authenticated else None
        
        success, message = cart.apply_coupon(code, user)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': success,
                'message': message,
                'cart_discount': str(cart.discount_amount),
                'cart_total': str(cart.total)
            })
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        
        return redirect('cart:detail')


class RemoveCouponView(CartMixin, View):
    """حذف کد تخفیف"""
    
    def post(self, request):
        cart = self.get_cart(request)
        cart.remove_coupon()
        
        message = 'کد تخفیف حذف شد'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': message,
                'cart_discount': '0',
                'cart_total': str(cart.total)
            })
        
        messages.success(request, message)
        return redirect('cart:detail')


class CartSummaryView(CartMixin, View):
    """خلاصه سبد خرید (برای header)"""
    
    def get(self, request):
        cart = self.get_cart(request)
        
        items = []
        for item in cart.items.select_related('product').prefetch_related('product__images')[:3]:
            image_url = ''
            if item.product.main_image:
                image_url = item.product.main_image.image.url
            
            items.append({
                'name': item.product.name,
                'quantity': item.quantity,
                'price': str(item.product.price),
                'total': str(item.total_price),
                'image': image_url,
                'url': item.product.get_absolute_url(),
            })
        
        return JsonResponse({
            'items': items,
            'items_count': cart.items_count,
            'subtotal': str(cart.subtotal),
            'discount': str(cart.discount_amount),
            'total': str(cart.total),
        })

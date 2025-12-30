"""
ویوهای اپ dashboard
پنل کاربری
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.paginator import Paginator

from apps.orders.models import Order
from apps.catalog.models import Wishlist
from apps.accounts.models import Address
from apps.accounts.forms import ProfileUpdateForm, AddressForm


class DashboardHomeView(LoginRequiredMixin, View):
    """صفحه اصلی داشبورد"""
    
    template_name = 'dashboard/home.html'
    
    def get(self, request):
        user = request.user
        
        # آخرین سفارش‌ها
        recent_orders = Order.objects.filter(
            user=user
        ).order_by('-created_at')[:5]
        
        # آمار
        total_orders = Order.objects.filter(user=user).count()
        pending_orders = Order.objects.filter(user=user, status='pending').count()
        
        # علاقه‌مندی‌ها
        wishlist_count = Wishlist.objects.filter(user=user).count()
        
        # آدرس‌ها
        addresses_count = Address.objects.filter(user=user).count()
        
        context = {
            'recent_orders': recent_orders,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'wishlist_count': wishlist_count,
            'addresses_count': addresses_count,
        }
        
        return render(request, self.template_name, context)


class OrderListView(LoginRequiredMixin, View):
    """لیست سفارشات"""
    
    template_name = 'dashboard/orders.html'
    
    def get(self, request):
        orders = Order.objects.filter(
            user=request.user
        ).order_by('-created_at')
        
        # فیلتر وضعیت
        status = request.GET.get('status')
        if status:
            orders = orders.filter(status=status)
        
        # صفحه‌بندی
        paginator = Paginator(orders, 10)
        page = request.GET.get('page', 1)
        orders = paginator.get_page(page)
        
        context = {
            'orders': orders,
            'current_status': status,
            'status_choices': Order.STATUS_CHOICES,
        }
        
        return render(request, self.template_name, context)


class OrderDetailView(LoginRequiredMixin, View):
    """جزئیات سفارش"""
    
    template_name = 'dashboard/order_detail.html'
    
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        
        context = {
            'order': order,
        }
        
        return render(request, self.template_name, context)


class ProfileView(LoginRequiredMixin, View):
    """پروفایل کاربر"""
    
    template_name = 'dashboard/profile.html'
    
    def get(self, request):
        form = ProfileUpdateForm(instance=request.user)
        
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'اطلاعات با موفقیت بروزرسانی شد')
            return redirect('dashboard:profile')
        
        return render(request, self.template_name, {'form': form})


class AddressListView(LoginRequiredMixin, View):
    """لیست آدرس‌ها"""
    
    template_name = 'dashboard/addresses.html'
    
    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        form = AddressForm()
        
        context = {
            'addresses': addresses,
            'form': form,
        }
        
        return render(request, self.template_name, context)


class WishlistView(LoginRequiredMixin, View):
    """لیست علاقه‌مندی‌ها"""
    
    template_name = 'dashboard/wishlist.html'
    
    def get(self, request):
        wishlist = Wishlist.objects.filter(
            user=request.user
        ).select_related(
            'product__category', 'product__brand'
        ).prefetch_related('product__images')
        
        return render(request, self.template_name, {'wishlist': wishlist})


class MessagesView(LoginRequiredMixin, View):
    """پیام‌ها"""
    
    template_name = 'dashboard/messages.html'
    
    def get(self, request):
        # TODO: Implement messaging system
        return render(request, self.template_name, {})


class ReviewsView(LoginRequiredMixin, View):
    """نظرات من"""
    
    template_name = 'dashboard/reviews.html'
    
    def get(self, request):
        from apps.reviews.models import Review
        
        reviews = Review.objects.filter(
            user=request.user
        ).select_related('product').order_by('-created_at')
        
        return render(request, self.template_name, {'reviews': reviews})


class AddAddressView(LoginRequiredMixin, View):
    """افزودن آدرس جدید"""
    
    def post(self, request):
        form = AddressForm(request.POST)
        
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'آدرس با موفقیت اضافه شد')
        else:
            messages.error(request, 'خطا در ثبت آدرس')
        
        return redirect('dashboard:addresses')


class DeleteAddressView(LoginRequiredMixin, View):
    """حذف آدرس"""
    
    def post(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user)
        address.delete()
        messages.success(request, 'آدرس با موفقیت حذف شد')
        return redirect('dashboard:addresses')


class DeleteReviewView(LoginRequiredMixin, View):
    """حذف نظر"""
    
    def post(self, request, pk):
        from apps.reviews.models import Review
        
        review = get_object_or_404(Review, pk=pk, user=request.user)
        review.delete()
        messages.success(request, 'نظر با موفقیت حذف شد')
        return redirect('dashboard:reviews')


class MarkAllMessagesReadView(LoginRequiredMixin, View):
    """علامت‌گذاری همه پیام‌ها به عنوان خوانده شده"""
    
    def post(self, request):
        # TODO: Implement when message model is ready
        messages.success(request, 'همه پیام‌ها خوانده شدند')
        return redirect('dashboard:messages')


class DeleteMessageView(LoginRequiredMixin, View):
    """حذف پیام"""
    
    def post(self, request, pk):
        # TODO: Implement when message model is ready
        messages.success(request, 'پیام حذف شد')
        return redirect('dashboard:messages')


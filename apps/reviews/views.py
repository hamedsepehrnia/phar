"""
ویوهای اپ reviews
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse

from .models import Review
from .forms import ReviewForm
from apps.catalog.models import Product


class AddReviewView(LoginRequiredMixin, View):
    """افزودن نظر"""
    
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        
        # بررسی نظر قبلی
        existing = Review.objects.filter(
            user=request.user,
            product=product
        ).exists()
        
        if existing:
            message = 'شما قبلاً برای این محصول نظر ثبت کرده‌اید'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': message})
            messages.error(request, message)
            return redirect(product.get_absolute_url())
        
        form = ReviewForm(request.POST)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            
            message = 'نظر شما ثبت شد و پس از بررسی نمایش داده خواهد شد'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': message})
            messages.success(request, message)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'خطا در ثبت نظر',
                    'errors': form.errors
                })
            messages.error(request, 'خطا در ثبت نظر')
        
        return redirect(product.get_absolute_url())


class DeleteReviewView(LoginRequiredMixin, View):
    """حذف نظر"""
    
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk, user=request.user)
        product_url = review.product.get_absolute_url()
        review.delete()
        
        messages.success(request, 'نظر حذف شد')
        return redirect(product_url)

"""
URLهای اپ cart
"""
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartView.as_view(), name='detail'),
    path('add/<int:product_id>/', views.AddToCartView.as_view(), name='add'),
    path('remove/<int:product_id>/', views.RemoveFromCartView.as_view(), name='remove'),
    path('update/<int:product_id>/', views.UpdateCartItemView.as_view(), name='update'),
    path('clear/', views.ClearCartView.as_view(), name='clear'),
    path('coupon/apply/', views.ApplyCouponView.as_view(), name='apply_coupon'),
    path('coupon/remove/', views.RemoveCouponView.as_view(), name='remove_coupon'),
    path('summary/', views.CartSummaryView.as_view(), name='summary'),
]

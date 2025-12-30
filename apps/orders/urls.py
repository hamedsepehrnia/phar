"""
URLهای اپ orders
"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('payment/<int:pk>/', views.PaymentView.as_view(), name='payment'),
    path('payment/callback/', views.PaymentCallbackView.as_view(), name='payment_callback'),
    path('payment/<int:pk>/success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/<int:pk>/failed/', views.PaymentFailedView.as_view(), name='payment_failed'),
    path('cancel/<int:pk>/', views.CancelOrderView.as_view(), name='cancel'),
]

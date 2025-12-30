"""
URLهای اپ accounts
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # احراز هویت
    path('login/', views.LoginView.as_view(), name='login'),
    path('verify/', views.VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', views.ResendOTPView.as_view(), name='resend_otp'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # آدرس‌ها
    path('addresses/', views.AddressListView.as_view(), name='addresses'),
    path('addresses/add/', views.AddressCreateView.as_view(), name='address_add'),
    path('addresses/<int:pk>/edit/', views.AddressUpdateView.as_view(), name='address_edit'),
    path('addresses/<int:pk>/delete/', views.AddressDeleteView.as_view(), name='address_delete'),
    path('addresses/<int:pk>/default/', views.SetDefaultAddressView.as_view(), name='address_default'),
]

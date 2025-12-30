"""
URLهای اپ dashboard
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),
    path('orders/', views.OrderListView.as_view(), name='orders'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('addresses/', views.AddressListView.as_view(), name='addresses'),
    path('addresses/add/', views.AddAddressView.as_view(), name='add_address'),
    path('addresses/delete/<int:pk>/', views.DeleteAddressView.as_view(), name='delete_address'),
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('messages/', views.MessagesView.as_view(), name='messages'),
    path('messages/mark-all-read/', views.MarkAllMessagesReadView.as_view(), name='mark_all_read'),
    path('messages/delete/<int:pk>/', views.DeleteMessageView.as_view(), name='delete_message'),
    path('reviews/', views.ReviewsView.as_view(), name='reviews'),
    path('reviews/delete/<int:pk>/', views.DeleteReviewView.as_view(), name='delete_review'),
]

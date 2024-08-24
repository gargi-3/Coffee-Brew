from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('coffees/', views.coffee_list, name='coffee_list'),
    path('coffees/<int:pk>/', views.coffee_detail, name='coffee_detail'),
    path('foods/', views.food_list, name='food_list'),
    path('foods/<int:pk>/', views.food_detail, name='food_detail'),
    path('add_to_cart/<str:item_type>/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/increase_quantity/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease_quantity/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('checkout/', views.order_create, name='order_create'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('search/', views.search, name='search'),
    # PWC
    # path('password_change/', views.password_change_view, name='password_change'),
    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='coffeeapp/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='coffeeapp/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='coffeeapp/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='coffeeapp/password_reset_complete.html'), name='password_reset_complete'),
]
from django.urls import path
from . import views


urlpatterns=[
    path('', views.login, name='login'),
    path('menu', views.menu, name='menu'),
    path('cart/', views.cart, name='cart'),
    path('order/', views.order, name='order'),
    path('payment/', views.payment, name='payment'),
    path('success/', views.success, name='success'),
]
from django.urls import path
from . import views


urlpatterns=[
    path('', views.login, name='login'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('logout/', views.logout_view, name='logout'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('menu/', views.menu, name='menu'),
    path("orders/", views.order_history, name="order_history"),
    path("chat/", views.chatbot, name="chat"),
    path('search_menu/', views.search_menu, name='search_menu'),
    path('cart/', views.cart, name='cart'),
    path('order/', views.order, name='order'),
    path('payment/', views.payment, name='payment'),
    path('success/', views.success, name='success'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('flower/<int:pk>/', views.flower_detail, name='flower_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:pk>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<int:pk>/', views.order_success, name='order_success'),
    path('orders/', views.my_orders, name='my_orders'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/flower/add/', views.flower_add, name='flower_add'),
    path('admin-panel/flower/edit/<int:pk>/', views.flower_edit, name='flower_edit'),
    path('admin-panel/flower/delete/<int:pk>/', views.flower_delete, name='flower_delete'),
]

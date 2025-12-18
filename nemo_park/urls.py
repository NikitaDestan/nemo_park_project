from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('employees/', views.employees_list, name='employees'),
    path('visitors/', views.visitors_list, name='visitors'),
    path('tickets/', views.tickets_list, name='tickets'),
    path('add-employee/', views.add_employee, name='add_employee'),
    path('add-visitor/', views.add_visitor, name='add_visitor'),
    path('add-ticket/', views.add_ticket, name='add_ticket'),
    path('edit-employee/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('delete-employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    path('edit-visitor/<int:visitor_id>/', views.edit_visitor, name='edit_visitor'),
    path('delete-visitor/<int:visitor_id>/', views.delete_visitor, name='delete_visitor'),
    path('edit-ticket/<int:ticket_id>/', views.edit_ticket, name='edit_ticket'),
    path('delete-ticket/<int:ticket_id>/', views.delete_ticket, name='delete_ticket'),
    
    # Товары
    path('products/', views.products_list, name='products'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    
    # Заказы
    path('orders/', views.orders_list, name='orders'),
    path('create-order/', views.create_order, name='create_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
    path('delete-order/<int:order_id>/', views.delete_order, name='delete_order'),
]
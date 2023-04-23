from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('reset_password/', views.reset_password, name='reset-password'),
    path('reset_password_validate/<uidb64>/<token>/', views.reset_password_validate, name='reset-password-validate'),
    path('reset_password_detail/', views.reset_password_detail, name='reset-password-detail'),
    path('my_orders/', views.my_orders , name='my-orders'),
    path('edit_profile/', views.edit_profile , name='edit-profile'),
    path('change_password/', views.change_password , name='change-password'),
    path('order_detail/<int:order_id>/', views.order_detail , name='order-detail'),
]
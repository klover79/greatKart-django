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
]
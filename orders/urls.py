from django.urls import path, include
from .import views

app_name = 'orders'

urlpatterns = [
    path('place_order/', views.place_order , name='place-order'),
    path('payments/', views.payments, name='payments'),
    path('order_completed/', views.order_completed, name='order-completed'),
     
]
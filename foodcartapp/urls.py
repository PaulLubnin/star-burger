from django.urls import path

from .views import product_list_api, banners_list_api, register_order

app_name = 'foodcartapp'

urlpatterns = [
    path('products/', product_list_api, name='product_list'),
    path('banners/', banners_list_api, name='banners_list'),
    path('order/', register_order, name='register_order'),
]

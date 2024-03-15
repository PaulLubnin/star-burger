from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, Client, OrderedProduct
from .serializers import ClientSerializer, OrderSerializer, OrderedProductSerializer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def create_client_object(incoming_order: dict) -> object:
    """Создание объекта Client."""

    client_serialization = ClientSerializer(data=incoming_order)
    client_serialization.is_valid(raise_exception=True)
    phonenumber = PhoneNumber.from_string(incoming_order.get('phonenumber'), region='RU')
    client, created = Client.objects.get_or_create(
        phonenumber=phonenumber.as_e164,
        defaults={
            'firstname': client_serialization.data.get('firstname'),
            'lastname': client_serialization.data.get('lastname')
        }
    )
    return client


def create_ordered_product_object(products: list, order: object):
    """Создание объекта OrderedProduct и добавление в Order."""

    for burger in products:
        burger['order'] = order.pk
        product_serialization = OrderedProductSerializer(data=burger)
        product_serialization.is_valid(raise_exception=True)
        OrderedProduct.objects.create(
            order_id=product_serialization.data.get('order'),
            product_id=product_serialization.data.get('product'),
            quantity=product_serialization.data.get('quantity'),
            strike_price=Product.objects.values_list('price', flat=True).get(
                pk=product_serialization.data.get('product'))
        )


def create_order_object(incoming_order: dict, client: object) -> object:
    """Создание объекта Order и добавление его к объекту Client."""

    order_serialization = OrderSerializer(data={**incoming_order, **{'client_id': client.pk}})
    order_serialization.is_valid(raise_exception=True)
    new_order_object = Order.objects.create(
        client=client,
        address=order_serialization.data.get('address'),
    )
    create_ordered_product_object(incoming_order.get('products'), new_order_object)
    return new_order_object


@api_view(http_method_names=('POST',))
def register_order(request):
    """Форма регистрации заказа."""

    try:
        incoming_order = request.data
        with transaction.atomic():
            client = create_client_object(incoming_order)
            order = create_order_object(incoming_order, client)
    except ValueError as error:
        return Response({'error': f'{error}'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as error:
        return Response({'error': f'{error}'}, status=status.HTTP_400_BAD_REQUEST)
    client_serializer = ClientSerializer(client)
    order_serializer = OrderSerializer(order)
    client_order = {**{'id': order_serializer.data.get('id')}, **client_serializer.data}
    return Response(client_order, status=status.HTTP_201_CREATED)

import requests
from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from geoplaces.views import create_place_object
from star_burger.settings import YANDEX_API_KEY
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


def create_client_object(incoming_order: dict) -> Client:
    """Создание объекта Client."""
    print('------create_client_object')
    print('***1')
    client_serialization = ClientSerializer(data=incoming_order)
    print('***2')
    client_serialization.is_valid(raise_exception=True)
    print('***3')
    phonenumber = PhoneNumber.from_string(incoming_order.get('phonenumber'), region='RU')
    print('***4')
    client, created = Client.objects.get_or_create(
        phonenumber=phonenumber.as_e164,
        defaults={
            'firstname': client_serialization.data.get('firstname'),
            'lastname': client_serialization.data.get('lastname')
        }
    )
    return client


def create_ordered_product_object(products: list, order: Order):
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
                pk=product_serialization.data.get('product')
            )
        )


def create_order_object(incoming_order: dict, client: Client) -> Order:
    """Создание объекта Order и добавление его к объекту Client."""
    print('-----create_order_object')
    print('***1')
    order_serialization = OrderSerializer(data={**incoming_order, **{'client_id': client.pk}})
    print('***2')
    order_serialization.is_valid(raise_exception=True)
    print('***3')
    address = order_serialization.data.get('address')
    print('***4')
    longitude, latitude = fetch_coordinates(YANDEX_API_KEY, address)
    print('***5')
    new_order_object = Order.objects.create(
        client=client,
        address=address,
        longitude=longitude,
        latitude=latitude
    )
    print('***6')
    create_ordered_product_object(incoming_order.get('products'), new_order_object)
    return new_order_object


def fetch_coordinates(api_key: str, address: str) -> tuple:
    """Получение координат."""
    print('-----fetch_coordinates')
    print('***1')
    base_url = 'https://geocode-maps.yandex.ru/1.x'
    print('***2')
    response = requests.get(base_url, params={
        'geocode': address,
        'apikey': api_key,
        'format': 'json',
    })
    print('***3')
    response.raise_for_status()
    print('***4')
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    print('-found_places:', found_places)
    print('---')
    print('-response.json()', response.json())
    print('***5')
    if not found_places:
        return None, None
    print('***6')
    most_relevant = found_places[0]
    # most_relevant = found_places[0]['GeoObject']
    # print('***7')
    # precision = most_relevant['metaDataProperty']['GeocoderMetaData'].get('precision')
    # print('***8')
    # if precision not in ('exact', 'number', 'near', 'street'):
    #     return None, None
    print('***9')
    longitude, latitude = most_relevant['GeoObject']['Point']['pos'].split(" ")
    print('=====fetch_coordinates')
    return longitude, latitude


@api_view(http_method_names=('POST',))
def register_order(request):
    """Форма регистрации заказа."""

    try:
        incoming_order = request.data
        print('incoming_order', request.data)
        with transaction.atomic():
            print('***client')
            client = create_client_object(incoming_order)
            print('client', client)
            order = create_order_object(incoming_order, client)
            print('order', order)
            place = create_place_object(order)  # дописать метод
    except (ValueError, Exception) as error:
        return Response({'error': f'{error}'}, status=status.HTTP_400_BAD_REQUEST)
    client_serialized = ClientSerializer(client)
    order_serialized = OrderSerializer(order)
    client_order = {**{'id': order_serialized.data.get('id')}, **client_serialized.data}
    return Response(client_order, status=status.HTTP_201_CREATED)

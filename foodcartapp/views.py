import json

from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.phonenumber import PhoneNumber

from .models import Product, Order, Client, OrderedProduct


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

    phonenumber = PhoneNumber.from_string(incoming_order['phonenumber'], region='RU')
    client, created = Client.objects.get_or_create(
        phonenumber=phonenumber.as_e164,
        defaults={
            'firstname': incoming_order['firstname'],
            'lastname': incoming_order['lastname']
        }
    )
    return client


def create_order_object(incoming_order: dict, client: object) -> object:
    """Создание объекта Order и добавление его к объекту Client."""

    new_order_object, created = Order.objects.get_or_create(
        address=incoming_order['address'],
        client=client,
    )
    if created:
        return new_order_object


def register_order(request):
    """Форма регистрации заказа."""

    try:
        order = json.loads(request.body.decode())
        client = create_client_object(order)
        if order['products']:
            new_order = create_order_object(order, client)
            if new_order:
                for burger in order['products']:
                    OrderedProduct.objects.create(
                        order=new_order,
                        product=Product.objects.get(id=burger['product']),
                        quantity=burger['quantity']
                    )
    except ValueError as error:
        return JsonResponse({
            'error': error,
        })
    return JsonResponse(order)

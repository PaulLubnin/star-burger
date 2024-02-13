from rest_framework import serializers
from phonenumber_field import serializerfields
from foodcartapp.models import Client, Order, OrderedProduct


class ClientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Client."""

    firstname = serializers.CharField(required=True, max_length=32)
    lastname = serializers.CharField(required=True, max_length=32)
    phonenumber = serializerfields.PhoneNumberField()

    class Meta:
        model = Client
        fields = ('id', 'firstname', 'lastname', 'phonenumber')


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор модели Order."""

    address = serializers.CharField(required=True)

    class Meta:
        model = Order
        fields = ('address', )


class OrderedProductSerializer(serializers.ModelSerializer):
    """Сериализатор модели OrderedProduct."""

    order = serializers.IntegerField(required=True)
    product = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True)

    class Meta:
        model = OrderedProduct
        fields = ('order', 'product', 'quantity')

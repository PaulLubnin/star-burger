# Generated by Django 3.2.15 on 2024-03-13 11:03

from django.db import migrations


def set_price_on_ordered_products(apps, schema_editor):
    """Добавление к старым заказам цены расчета."""

    OrderedProduct = apps.get_model('foodcartapp', 'OrderedProduct')
    for elem in OrderedProduct.objects.iterator():
        elem.strike_price = elem.product.price
        elem.save()


def move_backward(apps, schema_editor):
    """Отмена дата-миграции."""

    OrderedProduct = apps.get_model('foodcartapp', 'OrderedProduct')
    OrderedProduct.objects.update(strike_price=None)


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_orderedproduct_strike_price'),
    ]

    operations = [
        migrations.RunPython(set_price_on_ordered_products, move_backward),
    ]

from foodcartapp.models import Order
from geoplaces.models import Place


def get_normalized_address(dirty_address: str) -> str:
    """Нормализация адреса полученного от клиента."""

    return f'dirty: {dirty_address}'


def create_place_object(order: Order) -> Place:
    """Создание объекта Place."""

    address = order.address
    normalized_address = get_normalized_address(address)  # Дописать метод
    new_place_object = Place.objects.get_or_create(
        raw_address=address,
        normalized_address=normalized_address,
        longitude=order.longitude,
        latitude=order.latitude,
    )
    return new_place_object

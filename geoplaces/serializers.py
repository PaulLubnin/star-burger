from rest_framework import serializers

from geoplaces.models import Place


class PlaceSerializer(serializers.ModelSerializer):
    """Сериализатор модели Place."""

    raw_address = serializers.CharField(required=True)
    longitude = serializers.DecimalField(required=True, max_digits=9, decimal_places=6)
    latitude = serializers.DecimalField(required=True, max_digits=9, decimal_places=6)

    class Meta:
        model = Place
        fields = ('id', 'raw_address', 'longitude', 'latitude')

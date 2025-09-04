from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class Place(models.Model):
    """Сохраненные места и координаты места."""

    raw_address = models.CharField(
        verbose_name='Изначальный адрес введёный клиентом'
    )
    normalized_address = models.CharField(
        verbose_name='Нормализованный адрес',
        unique=True
    )
    longitude = models.DecimalField(
        verbose_name='Долгота',
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        db_index=True,
        blank=True,
        null=True
    )
    latitude = models.DecimalField(
        verbose_name='Широта',
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        db_index=True,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        default=timezone.now,
        db_index=True
    )
    changed_at = models.DateTimeField(
        verbose_name='Дата изменения',
        blank=True,
        null=True,
        db_index=True
    )

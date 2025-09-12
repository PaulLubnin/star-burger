from django.contrib import admin

from geoplaces.models import Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    pass

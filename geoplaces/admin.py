from django.contrib import admin

from geoplaces.models import Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)

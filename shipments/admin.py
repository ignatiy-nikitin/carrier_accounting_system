from django.contrib import admin

from shipments.models import Shipment


class ShipmentAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


admin.site.register(Shipment, ShipmentAdmin)

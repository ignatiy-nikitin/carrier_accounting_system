from django.contrib import admin

from orders.models import Order


class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'update')


admin.site.register(Order, OrderAdmin)

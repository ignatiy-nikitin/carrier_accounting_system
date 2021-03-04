from django.contrib import admin

from events.models import Event


class EventAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'datetime')


admin.site.register(Event, EventAdmin)

from django.contrib import admin

from boxes.models import Box


class BoxAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


admin.site.register(Box, BoxAdmin)

from django.contrib import admin

from companies.models import Company


class CompanyAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


admin.site.register(Company, CompanyAdmin)

from django.conf import settings
from django.db import models


class Shipment(models.Model):
    waybill_num = models.CharField(max_length=128)
    waybill_date = models.DateTimeField()
    comment = models.TextField(blank=True)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='shipments')

    def __str__(self):
        return f'Номер накладной: {self.waybill_num}'

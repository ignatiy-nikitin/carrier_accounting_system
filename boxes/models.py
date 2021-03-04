from django.db import models
from django.utils.translation import ugettext as _

from orders.models import Order
from shipments.models import Shipment


class Box(models.Model):
    class StatusChoices(models.TextChoices):
        NEW = 'NEW', 'Новый заказ'
        READY_FOR_SHIPPING = 'READY_FOR_SHIPPING', 'Собран на складе отправителя'
        SORTING = 'SORTING', 'На складе транспортной компании'
        DELIVERING = 'DELIVERING', 'Доставляется (передан курьеру для доставки покупателю)'
        DELAYED = 'DELAYED', 'Доставка не была выполнена в срок'
        DONE = 'DONE', 'Доставлен'
        CANCELED = 'CANCELED', 'Отменен'

    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='boxes',
                              verbose_name='Идентификатор заказа')
    client_code = models.CharField(max_length=64, unique=True, verbose_name='Код коробки в системе заказчика')
    code = models.CharField(max_length=256, verbose_name='Маркировка')
    width = models.FloatField(null=True, blank=True, verbose_name='Ширина', help_text='Метры')
    height = models.FloatField(null=True, blank=True, verbose_name='Высота', help_text='Метры')
    length = models.FloatField(null=True, blank=True, verbose_name='Длина', help_text='Метры')
    weight = models.FloatField(null=True, blank=True, verbose_name='Вес', help_text='Общий вес в кг')
    content_description = models.TextField(null=True, blank=True, verbose_name='Описание содержимого')
    status = models.CharField(max_length=32, choices=StatusChoices.choices, default=StatusChoices.NEW,
                              verbose_name='Состояние коробки', help_text='По умолчанию: NEW')
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='boxes', null=True, blank=True,
                                 verbose_name='Отправление', help_text='Указывается при создании отправления')

    class Meta:
        verbose_name = _('box')
        verbose_name_plural = _('boxes')

    def __str__(self):
        return self.client_code

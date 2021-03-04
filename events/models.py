from django.conf import settings
from django.db import models

from orders.models import Order


class Event(models.Model):
    class StatusChoices(models.TextChoices):
        NEW = 'NEW', 'Новый заказ'
        READY_FOR_SHIPPING = 'READY_FOR_SHIPPING', 'Собран на складе отправителя'
        SORTING = 'SORTING', 'На складе транспортной компании'
        DELIVERING = 'DELIVERING', 'Доставляется (передан курьеру для доставки покупателю)'
        DELAYED = 'DELAYED', 'Доставка не была выполнена в срок'
        DONE = 'DONE', 'Доставлен'
        CANCELED = 'CANCELED', 'Отменен'

    status = models.CharField(max_length=64, choices=StatusChoices.choices)  # choice?
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)  # auto_now_add?
    comments = models.TextField(blank=True)
    # пользователь системы, создавший событие?
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events')

    def __str__(self):
        return f'Пользователь: {self.user.username}, статус: {self.status}, дата: {self.datetime.astimezone()}'


# create own app?
class File(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=256)
    path = models.CharField(max_length=256)

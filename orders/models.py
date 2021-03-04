from django.conf import settings
from django.db import models

from companies.models import Company


class Order(models.Model):
    STATUS_CHOICES = {
        ('NEW', 'Новый заказ'),
        ('READY_FOR_SHIPPING', 'Собран на складе отправителя'),
        ('SORTING', 'На складе транспортной компании'),
        ('DELIVERING', 'Доставляется (передан курьеру для доставки покупателю)'),
        ('DELAYED', 'Доставка не была выполнена в срок'),
        ('DONE', 'Доставлен'),
        ('CANCELED', 'Отменен'),
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders',
                             verbose_name='Пользователь системы', help_text='Пользователь, создавший заказ')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True,
                                verbose_name='Компания',
                                help_text='Компания, к которой принадлежит пользователь, создавший документ')
    logistic_tracking = models.CharField(max_length=32, unique=True,
                                         verbose_name='Номер заявки в системе транспортной компании',
                                         help_text='Генерируется в системе')
    client_tracking = models.CharField(max_length=64,
                                       verbose_name='Номер заявки в системе отправителя',
                                       help_text='Уникальный для каждого заказа')
    client_name = models.CharField(max_length=264, blank=True, verbose_name='Грузоотправитель',
                                   help_text='Название организации')
    shipping_date = models.DateField(null=True, verbose_name='Ожидаемая дата подачи транспорта')
    shipping_time = models.TimeField(null=True, verbose_name='Ожидаемое время подачи транспорта')
    shipping_from = models.TextField(blank=True, verbose_name='Адрес загрузки транспорта')
    shipping_car_type = models.CharField(max_length=264, verbose_name='Формат предоставлемой машины')
    shipping_method = models.CharField(max_length=128, default='auto', verbose_name='Способ доставки',
                                       help_text='По умолчанию: auto')
    recipient_order_num = models.CharField(max_length=64, verbose_name='Номер заказа клиента')
    cargo_description = models.CharField(max_length=264, blank=True, verbose_name='Груз: описание')
    cargo_pallet = models.IntegerField(null=True, verbose_name='Груз: кол-во, паллет')
    cargo_qty = models.IntegerField(null=True, verbose_name='Груз: кол-во мест')
    cargo_weight = models.FloatField(null=True, verbose_name='Груз: масса', help_text='кг')
    cargo_price = models.CharField(max_length=128, blank=True, verbose_name='Стоимость груза', help_text='руб.')
    recipient_id = models.CharField(max_length=128, blank=True,
                                    verbose_name='Идентификатор в базе клиента')
    recipient_zip = models.CharField(max_length=128, blank=True, verbose_name='Адрес получателя: почтовый индекс')
    recipient_city = models.CharField(max_length=128, blank=True, verbose_name='Адрес получателя: город')
    recipient_email = models.EmailField(blank=True, verbose_name='Адрес получателя: электронная почта')
    recipient_area = models.CharField(max_length=128, blank=True, verbose_name='Адрес получателя: область')
    recipient_address = models.CharField(max_length=256, blank=True, verbose_name='Адрес получателя: адрес')
    recipient_address_comment = models.TextField(blank=True, verbose_name='Адрес получателя: комментарий')
    recipient_phone = models.TextField(blank=True, verbose_name='Телефон получателя')
    recipient_name = models.CharField(blank=True, max_length=264, verbose_name='ФИО получателя')
    recipient_name2 = models.CharField(blank=True, max_length=264,
                                       verbose_name='ФИО получателя. Альтернативный получатель')
    update = models.DateTimeField(auto_now_add=True, verbose_name='Дата последнего изменения заказа')
    comments = models.TextField(blank=True, verbose_name='Комментарии к заказу')

    @property
    def status(self):
        return list(set(box.status for box in self.boxes.all()))

    # status.fget.help_text = u'Все статусы коробок, включенных в заказ'

    def __str__(self):
        return f'Номер заявки: {self.logistic_tracking}'

    # def validate_unique(self, exclude=None):
    #     if Order.objects.filter(client_tracking=self.client_tracking, user__company_id=self.user.company_id).exists():
    #         raise ValidationError({
    #             'client_tracking': 'The company already has an order with this number. Unable to add order.'
    #         })
    #
    # def save(self, *args, **kwargs):
    #     self.validate_unique()
    #     super(Order, self).save(*args, **kwargs)

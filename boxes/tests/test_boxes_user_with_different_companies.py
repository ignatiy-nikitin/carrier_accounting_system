from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from companies.models import Company
from orders.models import Order


class BoxViewCreateTestCase(APITestCase):
    def setUp(self) -> None:
        self.company1 = Company.objects.create(name='Компания 1')
        self.company2 = Company.objects.create(name='Компания 2')

        self.user1 = get_user_model().objects.create(username='user1', company=self.company1)
        self.user2 = get_user_model().objects.create(username='user2', company=self.company2)

        self.order_of_user1 = Order.objects.create(
            client_tracking='1',
            recipient_order_num='1',
            user=self.user1,
            company=self.user1.company,
            logistic_tracking='1',
        )

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('box:box-list')

    def test_add_box_to_order_of_another_company(self):
        """Нельзя добавлять коробки к заказу, который был создан другой компанией,
        чем компания пользователя
        1. Пользователь 1 создает заказ 1. Пользователь 1 принадлежит компании 1
        2. Пользователь 2 создает коробки. Пользователь 2 принадлежит компании 2
        3. Пользователь 2 пытается добавить коробки к заказу 1:
        выдача ошикби добавления"""
        data = {
            'order_id': self.order_of_user1.id,
            'client_code': '1',
            'code': '1',
        }
        self.client.force_authenticate(self.user2)
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(),
                         {'order_id': ["An order with this id does not belong to the user's company."]})

    def test_boxes_only_your_company(self):
        """
        Получение коробок тоько своей компании.
        1. Созадать пользователя 1 компании 1
        2. Создать пользователя 2 компании 2
        3. Проверить, что пользователь 1 получает только коробки комппании 1
        3. Проверить, что пользователь 2 получает только коробки компании 2
        """
        pass

# TODO: тесты для retrieve аналогичные list

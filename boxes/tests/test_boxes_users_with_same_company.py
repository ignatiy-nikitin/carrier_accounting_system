"""
Тестирования фугкционала с учетом компаний пользователей: пользователи одной компании.
"""
import random
import string

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from boxes.models import Box
from companies.models import Company
from orders.models import Order


class BoxViewListTestCase(APITestCase):
    def setUp(self) -> None:
        self.company = Company.objects.create(name='Компания 1')
        self.user1 = get_user_model().objects.create(username='user1', company=self.company)
        self.user2 = get_user_model().objects.create(username='user2', company=self.company)
        self.order_of_user1 = Order.objects.create(
            client_tracking='1',
            recipient_order_num='1',
            user=self.user1,
            company=self.user1.company,
            logistic_tracking='1',
        )
        self.order_of_user2 = Order.objects.create(
            client_tracking='2',
            recipient_order_num='2',
            user=self.user2,
            company=self.user2.company,
            logistic_tracking='2'
        )
        self.boxes_of_user1 = [Box.objects.create(
            order=self.order_of_user1,
            client_code=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            code=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            width=random.uniform(1, 10000),
            height=random.uniform(1, 10000),
            length=random.uniform(1, 10000),
            weight=random.uniform(1, 10000),
            content_description=''.join(random.choice(string.ascii_lowercase) for _ in range(100)),
        ) for _ in range(10)]
        self.boxes_of_user2 = [Box.objects.create(
            order=self.order_of_user2,
            client_code=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            code=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            width=random.uniform(1, 10000),
            height=random.uniform(1, 10000),
            length=random.uniform(1, 10000),
            weight=random.uniform(1, 10000),
            content_description=''.join(random.choice(string.ascii_lowercase) for _ in range(100)),
        ) for _ in range(10)]
        self.boxes_of_both_users = self.boxes_of_user1 + self.boxes_of_user2

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('box:box-list')

    def test_get_boxes_from_different_orders(self):
        """Получение всего списка коробок, которые принадлежат компании. (Разные заказы у обоих пользователей)
        1. Пользователь 1 создает заказ, добавляет свои коробки
        2. Пользователь 2 создает заказ, добавлет свои коробки
        3. Проверка: поьзователь 1 получает все коробки (1 + 2)
        4. Провеока: пользователь 2 получает все коробки (1 + 2)"""
        self.client.force_authenticate(self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], len(self.boxes_of_both_users))
        self.assertEqual(
            data['results'],
            [
                {
                    'id': box.id,
                    'order': box.order.id,
                    'client_code': box.client_code,
                    'code': box.code,
                    'width': box.width,
                    'height': box.height,
                    'weight': box.weight,
                    'length': box.length,
                    'content_description': box.content_description,
                    'status': str(box.status),
                    'shipment': None,
                } for box in self.boxes_of_both_users[:len(data['results'])]
            ]
        )

        self.client.force_authenticate(self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], len(self.boxes_of_both_users))
        self.assertEqual(
            data['results'],
            [
                {
                    'id': box.id,
                    'order': box.order.id,
                    'client_code': box.client_code,
                    'code': box.code,
                    'width': box.width,
                    'height': box.height,
                    'weight': box.weight,
                    'length': box.length,
                    'content_description': box.content_description,
                    'status': str(box.status),
                    'shipment': None,
                } for box in self.boxes_of_both_users[:len(data['results'])]
            ]
        )

    def test_get_boxes_from_same_order(self):
        """Получение всего списка коробок, которые принадлежат компании. (Один заказ у обоих пользователей)
           1. Пользователь 1 добавляет свои коробки в заказ 1
           2. Пользователь 2 добавляет свои коробки в заказ 1
           3. Проверка: поьзователь 1 получает все коробки (1 + 2)
           4. Провеока: пользователь 2 получает все коробки (1 + 2)"""
        # переопределение заказа для коообок пользователя 2
        for box in self.boxes_of_user2:
            box.order = self.order_of_user1

        self.client.force_authenticate(self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], len(self.boxes_of_both_users))
        self.assertEqual(
            data['results'],
            [
                {
                    'id': box.id,
                    'order': box.order.id,
                    'client_code': box.client_code,
                    'code': box.code,
                    'width': box.width,
                    'height': box.height,
                    'weight': box.weight,
                    'length': box.length,
                    'content_description': box.content_description,
                    'status': str(box.status),
                    'shipment': None,
                } for box in self.boxes_of_both_users[:len(data['results'])]
            ]
        )

        self.client.force_authenticate(self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], len(self.boxes_of_both_users))
        self.assertEqual(
            data['results'],
            [
                {
                    'id': box.id,
                    'order': box.order.id,
                    'client_code': box.client_code,
                    'code': box.code,
                    'width': box.width,
                    'height': box.height,
                    'weight': box.weight,
                    'length': box.length,
                    'content_description': box.content_description,
                    'status': str(box.status),
                    'shipment': None,
                } for box in self.boxes_of_both_users[:len(data['results'])]
            ]
        )


# TODO: тесты для retrieve аналогичные list

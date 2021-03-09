from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from companies.models import Company
from orders.models import Order


class OrderViewListTestCase(APITestCase):
    def setUp(self) -> None:
        self.company1 = Company.objects.create(name='Компания 1')
        self.company2 = Company.objects.create(name='Компания 2')
        self.transoprt_company = Company.objects.create(name='Транспортная компания', is_transport_company=True)

        self.user1 = get_user_model().objects.create(username='user1', company=self.company1)
        self.user2 = get_user_model().objects.create(username='user2', company=self.company2)
        self.user_of_transport_company = get_user_model().objects.create(username='user_of_transport_company',
                                                                         company=self.transoprt_company)

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('order:order-list')

    def test(self):
        """Пользователь транспортной компании должен получать все заказы,
        остальные пользователи получают заказы только своей компании"""
        self.order1 = Order.objects.create(
            client_tracking='1',
            recipient_order_num='1',
            logistic_tracking='1',
            user=self.user1,
            company=self.user1.company,
        )
        self.order2 = Order.objects.create(
            client_tracking='2',
            recipient_order_num='2',
            logistic_tracking='2',
            user=self.user2,
            company=self.user2.company,
        )
        self.order3 = Order.objects.create(
            client_tracking='3',
            recipient_order_num='3',
            logistic_tracking='3',
            user=self.user_of_transport_company,
            company=self.user_of_transport_company.company,
        )

        self.client.force_authenticate(self.user_of_transport_company)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 3)

        self.client.force_authenticate(self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 1)

        self.client.force_authenticate(self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 1)
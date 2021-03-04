import random
import string

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from boxes.models import Box
from companies.models import Company
from orders.models import Order
from shipments.models import Shipment


def get_random_date():
    result = str(random.randint(2000, 2020)) + '-'
    result += str(random.randint(1, 12)).zfill(2) + '-'
    result += str(random.randint(1, 28)).zfill(2)
    return result


def get_random_time():
    return str(random.randint(0, 23)).zfill(2) + ':' + str(random.randint(0, 59)).zfill(2) + ':00'


def get_random_datetime():
    return get_random_date() + 'T' + get_random_time()


class ShipmentViewCreateTestCase(APITestCase):
    def setUp(self) -> None:
        self.company = Company.objects.create(name='Компания 1')
        self.recipient_company = Company.objects.create(name='Компания получателя')
        self.user = get_user_model().objects.create(username='user1', company=self.company)
        self.order = Order.objects.create(
            client_tracking='1',
            recipient_order_num='1',
            user=self.user,
            company=self.user.company,
            recipient_company_id=self.recipient_company.id,
        )
        self.boxes = [Box.objects.create(
            order=self.order,
            client_code=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            code=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            width=random.uniform(1, 10000),
            height=random.uniform(1, 10000),
            length=random.uniform(1, 10000),
            weight=random.uniform(1, 10000),
            content_description=''.join(random.choice(string.ascii_lowercase) for _ in range(100)),
        ) for _ in range(10)]

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('shipment:shipment-list')

    def test_unauthorised(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"detail": "Authentication credentials were not provided."})

    def test_user_blocked(self):
        self.user.blocked = True
        self.user.save()
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'detail': 'User blocked by administrator.'})

    def test_empty_create(self):
        self.maxDiff = None

        data = {}
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        field_required_message = 'This field is required.'
        print(response.json())
        self.assertEqual(
            response.json(),
            {
                'waybill_num': [field_required_message],
                'waybill_date': [field_required_message],
                'boxes_ids': [field_required_message],
            }
        )

    # TODO: проверка на добавление корбок только своей компании

    def test(self):
        data = {
            'waybill_num': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            'waybill_date': get_random_datetime(),
            'comment': ''.join(random.choice(string.ascii_lowercase) for _ in range(100)),
            'boxes_ids': [box.id for box in self.boxes],
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data=data)
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        shipment = Shipment.objects.get()
        print(shipment)
        self.assertEqual(
            response.json(),
            {
                'id': shipment.id,
            }
        )
        # response = self.cient.post()

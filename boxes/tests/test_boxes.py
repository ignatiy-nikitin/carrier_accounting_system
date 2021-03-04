import random
import string

from django.contrib.auth import get_user_model
from django.forms import model_to_dict
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from boxes.models import Box
from orders.models import Order


class BoxViewCreateTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create()
        self.order = Order.objects.create(
            client_tracking='1',
            recipient_order_num='1',
            user=self.user,
        )

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('box:box-list')

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
        """Проверка вывода обязательных полей"""
        data = {}
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        field_required_message = 'This field is required.'
        self.assertEqual(
            response.json(),
            {
                'order_id': [field_required_message],
                'client_code': [field_required_message],
                'code': [field_required_message],
            }
        )

    def test(self):
        data = {
            'order_id': self.order.id,
            'client_code': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            'code': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            'width': random.uniform(1, 10000),
            'height': random.uniform(1, 10000),
            'length': random.uniform(1, 10000),
            'weight': random.uniform(1, 10000),
            'content_description': ''.join(random.choice(string.ascii_lowercase) for _ in range(100)),
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        box = Box.objects.get()
        data.pop('order_id')
        self.assertEqual(
            response.json(),
            {
                'id': box.id,
                'order': self.order.id,
                'status': str(Box.StatusChoices.NEW),
                'shipment': None,
                **data
            }
        )
        self.assertEqual(
            model_to_dict(box),
            {
                'id': box.id,
                'order': self.order.id,
                'client_code': data['client_code'],
                'code': data['code'],
                'width': data['width'],
                'height': data['height'],
                'length': data['length'],
                'weight': data['weight'],
                'content_description': data['content_description'],
                'status': str(Box.StatusChoices.NEW),
                'shipment': None,
            }
        )


class BoxViewListTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create()
        self.order = Order.objects.create(
            client_tracking='1',
            recipient_order_num='1',
            user=self.user,
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
        cls.url = reverse('box:box-list')

    def test_unauthorised(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"detail": "Authentication credentials were not provided."})

    def test_user_blocked(self):
        self.user.blocked = True
        self.user.save()
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'detail': 'User blocked by administrator.'})

    def test(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], len(self.boxes))
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
                } for box in self.boxes[:len(data['results'])]
            ]
        )


class BoxViewRetrieveTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create()
        self.order = Order.objects.create(
            client_tracking='1',
            recipient_order_num='1',
            user=self.user,
        )
        self.box = Box.objects.create(
            order=self.order,
            client_code=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            code=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            width=random.uniform(1, 10000),
            height=random.uniform(1, 10000),
            length=random.uniform(1, 10000),
            weight=random.uniform(1, 10000),
            content_description=''.join(random.choice(string.ascii_lowercase) for _ in range(100)),
        )
        self.url = reverse('box:box-detail', kwargs={'pk': self.box.id})

    def test_unauthorised(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"detail": "Authentication credentials were not provided."})

    def test_user_blocked(self):
        self.user.blocked = True
        self.user.save()
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'detail': 'User blocked by administrator.'})

    def test(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                'id': self.box.id,
                'order': self.box.order.id,
                'client_code': self.box.client_code,
                'code': self.box.code,
                'width': self.box.width,
                'height': self.box.height,
                'weight': self.box.weight,
                'length': self.box.length,
                'content_description': self.box.content_description,
                'status': str(self.box.status),
                'shipment': None,
            }
        )


class BoxViewUpdateTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create()
        self.order = Order.objects.create(
            client_tracking='1',
            recipient_order_num='1',
            user=self.user,
        )
        self.box = Box.objects.create(
            order=self.order,
            client_code=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            code=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            width=random.uniform(1, 10000),
            height=random.uniform(1, 10000),
            length=random.uniform(1, 10000),
            weight=random.uniform(1, 10000),
            content_description=''.join(random.choice(string.ascii_lowercase) for _ in range(100)),
        )
        self.url = reverse('box:box-detail', kwargs={'pk': self.box.id})

    def test_unauthorised_put(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"detail": "Authentication credentials were not provided."})

    def test_user_blocked(self):
        self.user.blocked = True
        self.user.save()
        self.client.force_authenticate(self.user)

        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'detail': 'User blocked by administrator.'})

        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'detail': 'User blocked by administrator.'})

    def test_unauthorised_patch(self):
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"detail": "Authentication credentials were not provided."})

    def test_empty_update_put(self):
        data = {}
        self.client.force_authenticate(self.user)
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                'id': self.box.id,
                'order': self.box.order.id,
                'client_code': self.box.client_code,
                'code': self.box.code,
                'width': self.box.width,
                'height': self.box.height,
                'weight': self.box.weight,
                'length': self.box.length,
                'content_description': self.box.content_description,
                'status': str(self.box.status),
                'shipment': None,
            }
        )

    def test_empty_update_patch(self):
        data = {}
        self.client.force_authenticate(self.user)
        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                'id': self.box.id,
                'order': self.box.order.id,
                'client_code': self.box.client_code,
                'code': self.box.code,
                'width': self.box.width,
                'height': self.box.height,
                'weight': self.box.weight,
                'length': self.box.length,
                'content_description': self.box.content_description,
                'status': str(self.box.status),
                'shipment': None,
            }
        )

    def test_full_update(self):
        new_order = Order.objects.create(
            client_tracking='2',
            recipient_order_num='2',
            user=self.user,
            logistic_tracking='unique value'
        )
        data = {
            'order_id': new_order.id,
            'client_code': self.box.client_code + ' updated',
            'code': self.box.code + ' updated',
            'width': self.box.width + 100,
            'height': self.box.height + 100,
            'length': self.box.length + 100,
            'weight': self.box.weight + 100,
            'content_description': self.box.content_description + ' updated',
        }
        self.client.force_authenticate(self.user)
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                'id': self.box.id,
                'order': new_order.id,
                'client_code': data['client_code'],
                'code': data['code'],
                'width': data['width'],
                'height': data['height'],
                'weight': data['weight'],
                'length': data['length'],
                'content_description': data['content_description'],
                'status': str(self.box.status),
                'shipment': None,
            }
        )

    def test_update_without_order_id(self):
        """Обновление всех полей, кроме order_id"""
        data = {
            'client_code': self.box.client_code + ' updated',
            'code': self.box.code + ' updated',
            'width': self.box.width + 100,
            'height': self.box.height + 100,
            'length': self.box.length + 100,
            'weight': self.box.weight + 100,
            'content_description': self.box.content_description + ' updated',
        }
        self.client.force_authenticate(self.user)
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                'id': self.box.id,
                'order': self.box.order.id,
                'client_code': data['client_code'],
                'code': data['code'],
                'width': data['width'],
                'height': data['height'],
                'weight': data['weight'],
                'length': data['length'],
                'content_description': data['content_description'],
                'status': str(self.box.status),
                'shipment': None,
            }
        )

    def test_impossibility_of_updating_status(self):
        """Поле status только на чтение"""
        data = {
            'status': random.choice(Box.StatusChoices.choices)[0]
        }
        self.client.force_authenticate(self.user)
        response = self.client.patch(self.url, data=data)
        # print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # проверка, что ничего не поменялось
        self.assertEqual(
            response.json(),
            {
                'id': self.box.id,
                'order': self.box.order.id,
                'client_code': self.box.client_code,
                'code': self.box.code,
                'width': self.box.width,
                'height': self.box.height,
                'weight': self.box.weight,
                'length': self.box.length,
                'content_description': self.box.content_description,
                'status': str(self.box.status),
                'shipment': None,
            }
        )


class BoxViewDeleteTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create()
        self.order = Order.objects.create(
            client_tracking='1',
            recipient_order_num='1',
            user=self.user,
        )
        self.box = Box.objects.create(
            order=self.order,
            client_code=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            code=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            width=random.uniform(1, 10000),
            height=random.uniform(1, 10000),
            length=random.uniform(1, 10000),
            weight=random.uniform(1, 10000),
            content_description=''.join(random.choice(string.ascii_lowercase) for _ in range(100)),
        )
        self.url = reverse('box:box-detail', kwargs={'pk': self.box.id})

    def test_unauthorised(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"detail": "Authentication credentials were not provided."})

    def test_user_blocked(self):
        self.user.blocked = True
        self.user.save()
        self.client.force_authenticate(self.user)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'detail': 'User blocked by administrator.'})

    def test(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)
        self.assertRaises(Box.DoesNotExist, Box.objects.get, id=self.box.id)

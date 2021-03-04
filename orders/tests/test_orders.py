import random
import string

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from companies.models import Company
from orders.models import Order
from users.models import User


def get_random_date():
    result = str(random.randint(2000, 2020)) + '-'
    result += str(random.randint(1, 12)).zfill(2) + '-'
    result += str(random.randint(1, 28)).zfill(2)
    return result


def get_random_time():
    return str(random.randint(0, 23)).zfill(2) + ':' + str(random.randint(0, 59)).zfill(2) + ':00'


def get_random_email():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(10)) + '@' + ''.join(
        random.choice(string.ascii_lowercase) for _ in range(10)) + '.' + random.choice(['ru', 'com', 'org'])


class OrderViewCreateTestCase(APITestCase):
    def setUp(self) -> None:
        self.company = Company.objects.create(name='Компания 1')
        self.user = get_user_model().objects.create(company=self.company)

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('order:order-list')

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

    def test(self):
        # self.maxDiff = None

        recipient_company = Company.objects.create(name='Компания получателя')
        data = {
            'client_tracking': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            'client_name': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            'shipping_date': get_random_date(),
            'shipping_time': get_random_time(),
            'shipping_from': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            'shipping_car_type': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            'recipient_order_num': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            'cargo_description': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            'cargo_pallet': random.randint(0, 1000),
            'cargo_qty': random.randint(0, 1000),
            'cargo_weight': random.uniform(0, 1000),
            'cargo_price': str(random.uniform(0, 1000)),  # цена указана как строка
            'recipient_company_id': recipient_company.id,
            'recipient_zip': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            'recipient_city': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            'recipient_email': get_random_email(),
            'recipient_area': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            'recipient_address': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            'recipient_address_comment': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            'recipient_phone': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            'recipient_name': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            'recipient_name2': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            'comments': ''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get()

        data.pop('recipient_company_id')
        response.json().pop('update')

        self.assertEqual(
            response.json(),
            {
                'id': order.id,
                'company': {
                    'id': self.user.company.id,
                    'name': self.user.company.name,
                },
                'shipping_method': 'auto',
                'logistic_tracking': order.logistic_tracking,
                'recipient_company': {'id': recipient_company.id, 'name': recipient_company.name},
                'status': [],
                'user': {
                    'username': self.user.username,
                    'name': self.user.name,
                    'email': self.user.email,
                    'company': {
                        'id': self.user.company.id,
                        'name': self.user.company.name,
                    }
                },
                **data
            }
        )

        # TODO: проверка занесения модели в бд

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
                'client_tracking': [field_required_message],
                'recipient_order_num': [field_required_message],
                'recipient_company_id': [field_required_message],
            }
        )


class OrderViewListTestCase(APITestCase):
    def setUp(self) -> None:
        self.company = Company.objects.create(name='Компания 1')
        self.user = get_user_model().objects.create(company=self.company)
        self.recipient_company = Company.objects.create(name='Компания получателя')
        self.orders = [Order.objects.create(
            client_tracking=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            client_name=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            shipping_date=get_random_date(),
            shipping_time=get_random_time(),
            shipping_from=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            shipping_car_type=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_order_num=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            cargo_description=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            cargo_pallet=random.randint(0, 1000),
            cargo_qty=random.randint(0, 1000),
            cargo_weight=random.uniform(0, 1000),
            cargo_price=str(random.uniform(0, 1000)),  # цена указана как строка
            recipient_company_id=self.recipient_company.id,
            recipient_zip=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_city=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_email=get_random_email(),
            recipient_area=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_address=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_address_comment=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_phone=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_name=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_name2=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            comments=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            user=self.user,
            company=self.user.company,
            logistic_tracking=f'{i}',
        ) for i in range(20)]

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('order:order-list')

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
        self.maxDiff = None

        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], len(self.orders))

        for order in data['results']:
            order.pop('update')

        self.assertEqual(
            data['results'],
            [
                {
                    'id': order.id,
                    'company': {
                        'id': self.user.company.id,
                        'name': self.user.company.name,
                    },
                    'shipping_method': 'auto',
                    'logistic_tracking': order.logistic_tracking,
                    'recipient_company': {'id': self.recipient_company.id, 'name': self.recipient_company.name},
                    'status': [],
                    'user': {
                        'username': self.user.username,
                        'name': self.user.name,
                        'email': self.user.email,
                        'company': {
                            'id': self.user.company.id,
                            'name': self.user.company.name,
                        }
                    },
                    'client_tracking': order.client_tracking,
                    'client_name': order.client_name,
                    'shipping_date': order.shipping_date,
                    'shipping_time': order.shipping_time,
                    'shipping_from': order.shipping_from,
                    'shipping_car_type': order.shipping_car_type,
                    'recipient_order_num': order.recipient_order_num,
                    'cargo_description': order.cargo_description,
                    'cargo_pallet': order.cargo_pallet,
                    'cargo_qty': order.cargo_qty,
                    'cargo_weight': order.cargo_weight,
                    'cargo_price': order.cargo_price,  # цена указана как строка
                    'recipient_zip': order.recipient_zip,
                    'recipient_city': order.recipient_city,
                    'recipient_email': order.recipient_email,
                    'recipient_area': order.recipient_area,
                    'recipient_address': order.recipient_address,
                    'recipient_address_comment': order.recipient_address_comment,
                    'recipient_phone': order.recipient_phone,
                    'recipient_name': order.recipient_name,
                    'recipient_name2': order.recipient_name2,
                    'comments': order.comments,
                } for order in self.orders[:len(data['results'])]
            ]
        )


class OrderViewRetrieveTestCase(APITestCase):
    def setUp(self) -> None:
        self.company = Company.objects.create(name='Компания 1')
        self.user = get_user_model().objects.create(company=self.company)
        self.recipient_company = Company.objects.create(name='Компания получателя')
        self.order = Order.objects.create(
            client_tracking=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            client_name=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            shipping_date=get_random_date(),
            shipping_time=get_random_time(),
            shipping_from=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            shipping_car_type=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_order_num=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            cargo_description=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            cargo_pallet=random.randint(0, 1000),
            cargo_qty=random.randint(0, 1000),
            cargo_weight=random.uniform(0, 1000),
            cargo_price=str(random.uniform(0, 1000)),  # цена указана как строка
            recipient_company_id=self.recipient_company.id,
            recipient_zip=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_city=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_email=get_random_email(),
            recipient_area=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_address=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_address_comment=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_phone=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_name=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_name2=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            comments=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            user=self.user,
            company=self.user.company,
            logistic_tracking=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
        )
        self.url = reverse('order:order-detail', kwargs={'pk': self.order.id})

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

        response.json().pop('update')

        self.assertEqual(
            response.json(),
            {
                'id': self.order.id,
                'company': {
                    'id': self.user.company.id,
                    'name': self.user.company.name,
                },
                'shipping_method': 'auto',
                'logistic_tracking': self.order.logistic_tracking,
                'recipient_company': {'id': self.recipient_company.id, 'name': self.recipient_company.name},
                'status': [],
                'user': {
                    'username': self.user.username,
                    'name': self.user.name,
                    'email': self.user.email,
                    'company': {
                        'id': self.user.company.id,
                        'name': self.user.company.name,
                    }
                },
                'client_tracking': self.order.client_tracking,
                'client_name': self.order.client_name,
                'shipping_date': self.order.shipping_date,
                'shipping_time': self.order.shipping_time,
                'shipping_from': self.order.shipping_from,
                'shipping_car_type': self.order.shipping_car_type,
                'recipient_order_num': self.order.recipient_order_num,
                'cargo_description': self.order.cargo_description,
                'cargo_pallet': self.order.cargo_pallet,
                'cargo_qty': self.order.cargo_qty,
                'cargo_weight': self.order.cargo_weight,
                'cargo_price': self.order.cargo_price,  # цена указана как строка
                'recipient_zip': self.order.recipient_zip,
                'recipient_city': self.order.recipient_city,
                'recipient_email': self.order.recipient_email,
                'recipient_area': self.order.recipient_area,
                'recipient_address': self.order.recipient_address,
                'recipient_address_comment': self.order.recipient_address_comment,
                'recipient_phone': self.order.recipient_phone,
                'recipient_name': self.order.recipient_name,
                'recipient_name2': self.order.recipient_name2,
                'comments': self.order.comments,
            }
        )


class OrderViewUpdateTestCase(APITestCase):
    def setUp(self) -> None:
        self.company = Company.objects.create(name='Компания 1')
        self.user = get_user_model().objects.create(company=self.company)
        self.recipient_company = Company.objects.create(name='Компания получателя')
        self.order = Order.objects.create(
            client_tracking=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            client_name=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            shipping_date=get_random_date(),
            shipping_time=get_random_time(),
            shipping_from=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            shipping_car_type=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_order_num=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            cargo_description=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            cargo_pallet=random.randint(0, 1000),
            cargo_qty=random.randint(0, 1000),
            cargo_weight=random.uniform(0, 1000),
            cargo_price=str(random.uniform(0, 1000)),  # цена указана как строка
            recipient_company_id=self.recipient_company.id,
            recipient_zip=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_city=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_email=get_random_email(),
            recipient_area=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_address=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_address_comment=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_phone=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_name=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_name2=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            comments=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            user=self.user,
            company=self.user.company,
            logistic_tracking=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
        )
        self.url = reverse('order:order-detail', kwargs={'pk': self.order.id})

    def test_unauthorised(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"detail": "Authentication credentials were not provided."})

        response = self.client.patch(self.url)
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

    def test_empty_update_put(self):
        data = {}
        self.client.force_authenticate(self.user)
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # self.assertEqual(response.json().pop('update')
        # TODO: self.assertNotEquals(self.order.update, response.json().pop('update'))
        # print(self.order.update, response.json().pop('update'))

        self.assertEqual(
            response.json(),
            {
                'id': self.order.id,
                'company': {
                    'id': self.user.company.id,
                    'name': self.user.company.name,
                },
                'shipping_method': 'auto',
                'logistic_tracking': self.order.logistic_tracking,
                'recipient_company': {'id': self.recipient_company.id, 'name': self.recipient_company.name},
                'status': [],
                'user': {
                    'username': self.user.username,
                    'name': self.user.name,
                    'email': self.user.email,
                    'company': {
                        'id': self.user.company.id,
                        'name': self.user.company.name,
                    }
                },
                'client_tracking': self.order.client_tracking,
                'client_name': self.order.client_name,
                'shipping_date': self.order.shipping_date,
                'shipping_time': self.order.shipping_time,
                'shipping_from': self.order.shipping_from,
                'shipping_car_type': self.order.shipping_car_type,
                'recipient_order_num': self.order.recipient_order_num,
                'cargo_description': self.order.cargo_description,
                'cargo_pallet': self.order.cargo_pallet,
                'cargo_qty': self.order.cargo_qty,
                'cargo_weight': self.order.cargo_weight,
                'cargo_price': self.order.cargo_price,  # цена указана как строка
                'recipient_zip': self.order.recipient_zip,
                'recipient_city': self.order.recipient_city,
                'recipient_email': self.order.recipient_email,
                'recipient_area': self.order.recipient_area,
                'recipient_address': self.order.recipient_address,
                'recipient_address_comment': self.order.recipient_address_comment,
                'recipient_phone': self.order.recipient_phone,
                'recipient_name': self.order.recipient_name,
                'recipient_name2': self.order.recipient_name2,
                'comments': self.order.comments,
            }
        )

    def test_empty_update_patch(self):
        data = {}
        self.client.force_authenticate(self.user)
        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response.json().pop('update')

        self.assertEqual(
            response.json(),
            {
                'id': self.order.id,
                'company': {
                    'id': self.user.company.id,
                    'name': self.user.company.name,
                },
                'shipping_method': 'auto',
                'logistic_tracking': self.order.logistic_tracking,
                'recipient_company': {'id': self.recipient_company.id, 'name': self.recipient_company.name},
                'status': [],
                'user': {
                    'username': self.user.username,
                    'name': self.user.name,
                    'email': self.user.email,
                    'company': {
                        'id': self.user.company.id,
                        'name': self.user.company.name,
                    }
                },
                'client_tracking': self.order.client_tracking,
                'client_name': self.order.client_name,
                'shipping_date': self.order.shipping_date,
                'shipping_time': self.order.shipping_time,
                'shipping_from': self.order.shipping_from,
                'shipping_car_type': self.order.shipping_car_type,
                'recipient_order_num': self.order.recipient_order_num,
                'cargo_description': self.order.cargo_description,
                'cargo_pallet': self.order.cargo_pallet,
                'cargo_qty': self.order.cargo_qty,
                'cargo_weight': self.order.cargo_weight,
                'cargo_price': self.order.cargo_price,  # цена указана как строка
                'recipient_zip': self.order.recipient_zip,
                'recipient_city': self.order.recipient_city,
                'recipient_email': self.order.recipient_email,
                'recipient_area': self.order.recipient_area,
                'recipient_address': self.order.recipient_address,
                'recipient_address_comment': self.order.recipient_address_comment,
                'recipient_phone': self.order.recipient_phone,
                'recipient_name': self.order.recipient_name,
                'recipient_name2': self.order.recipient_name2,
                'comments': self.order.comments,
            }
        )

    def test_full_update(self):
        self.maxDiff = None
        new_company = Company.objects.create(name='Новая компания')
        new_user = User.objects.create(username='new_user', company=new_company)
        data = {
            'client_tracking': self.order.client_tracking + ' updated',
            'client_name': self.order.client_name + ' updated',
            'shipping_date': get_random_date(),
            'shipping_time': get_random_time(),
            'shipping_from': self.order.shipping_from + ' updated',
            'shipping_car_type': self.order.shipping_car_type + ' updated',
            'recipient_order_num': self.order.recipient_order_num + ' updated',
            'cargo_description': self.order.cargo_description + ' updated',
            'cargo_pallet': self.order.cargo_pallet + 100,
            'cargo_qty': self.order.cargo_qty + 100,
            'cargo_weight': self.order.cargo_weight + random.uniform(1, 10),
            'cargo_price': self.order.cargo_price + ' updated',
            'recipient_company_id': self.order.recipient_company.id,  # вероятно избычтоно (будет убрано из модели)
            'recipient_zip': self.order.recipient_zip + ' updated',
            'recipient_city': self.order.recipient_city + ' updated',
            'recipient_email': 'update@update.com',
            'recipient_area': self.order.recipient_area + ' updated',
            'recipient_address': self.order.recipient_address + ' update',
            'recipient_address_comment': self.order.recipient_address_comment + ' updated',
            'recipient_phone': self.order.recipient_phone + ' updated',
            'recipient_name': self.order.recipient_name + ' updated',
            'recipient_name2': self.order.recipient_name2 + ' updated',
            'comments': self.order.comments + ' updated',
            # поля, которые не должны обновиться
            'logistic_tracking': self.order.logistic_tracking + ' updated',
            'status': ['SOME_NEW_STATUS'],
            'company': new_company.id,
            'update': get_random_date(),
            'shipping_method': self.order.shipping_method + ' updated',
            'user': new_user,
        }
        self.client.force_authenticate(self.user)
        response = self.client.put(self.url, data=data)
        # print(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response.json().pop('update')

        self.assertEqual(
            response.json(),
            {
                'id': self.order.id,
                'company': {
                    'id': self.user.company.id,
                    'name': self.user.company.name,
                },
                'shipping_method': data['shipping_method'],
                'logistic_tracking': data['logistic_tracking'],
                'recipient_company': {'id': self.recipient_company.id, 'name': self.recipient_company.name},
                'status': [],
                'user': {
                    'username': self.user.username,
                    'name': self.user.name,
                    'email': self.user.email,
                    'company': {
                        'id': self.user.company.id,
                        'name': self.user.company.name,
                    }
                },
                'client_tracking': data['client_tracking'],
                'client_name': data['client_name'],
                'shipping_date': self.order.shipping_date,
                'shipping_time': self.order.shipping_time,
                'shipping_from': data['shipping_from'],
                'shipping_car_type': data['shipping_car_type'],
                'recipient_order_num': data['recipient_order_num'],
                'cargo_description': data['cargo_description'],
                'cargo_pallet': data['cargo_pallet'],
                'cargo_qty': data['cargo_qty'],
                'cargo_weight': data['cargo_weight'],
                'cargo_price': data['cargo_price'],  # цена указана как строка
                'recipient_zip': data['recipient_zip'],
                'recipient_city': data['recipient_city'],
                'recipient_email': data['recipient_email'],
                'recipient_area': data['recipient_area'],
                'recipient_address': data['recipient_address'],
                'recipient_address_comment': data['recipient_address_comment'],
                'recipient_phone': data['recipient_phone'],
                'recipient_name': data['recipient_name'],
                'recipient_name2': data['recipient_name2'],
                'comments': data['comments'],
            }
        )


class OrderViewDeleteTestCase(APITestCase):
    def setUp(self) -> None:
        self.company = Company.objects.create(name='Компания 1')
        self.user = get_user_model().objects.create(company=self.company)
        self.recipient_company = Company.objects.create(name='Компания получателя')
        self.order = Order.objects.create(
            client_tracking=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            client_name=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            shipping_date=get_random_date(),
            shipping_time=get_random_time(),
            shipping_from=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            shipping_car_type=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_order_num=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            cargo_description=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            cargo_pallet=random.randint(0, 1000),
            cargo_qty=random.randint(0, 1000),
            cargo_weight=random.uniform(0, 1000),
            cargo_price=str(random.uniform(0, 1000)),  # цена указана как строка
            recipient_company_id=self.recipient_company.id,
            recipient_zip=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_city=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_email=get_random_email(),
            recipient_area=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_address=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_address_comment=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_phone=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_name=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            recipient_name2=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            comments=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
            user=self.user,
            company=self.user.company,
            logistic_tracking=''.join(random.choice(string.ascii_lowercase) for _ in range(10)),
        )
        self.url = reverse('order:order-detail', kwargs={'pk': self.order.id})

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
        self.assertRaises(Order.DoesNotExist, Order.objects.get, id=self.order.id)

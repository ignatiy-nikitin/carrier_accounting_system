from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from companies.models import Company
from companies.serializers import CompanySerializer
from events.models import Event
from orders.models import Order
from orders.utils import generate_logistic_tracking
from users.serializers import UserListRetrieveSerializer


class OrderListRetrieveSerializer(serializers.ModelSerializer):
    user = UserListRetrieveSerializer()
    company = CompanySerializer()

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'company',
            'logistic_tracking', 'client_tracking', 'client_name',
            'shipping_date', 'shipping_time', 'shipping_from',
            'shipping_car_type', 'shipping_method', 'recipient_order_num',
            'cargo_description', 'cargo_pallet', 'cargo_qty',
            'cargo_weight', 'cargo_price', 'recipient_id',
            'recipient_zip', 'recipient_city', 'recipient_email',
            'recipient_area', 'recipient_address', 'recipient_address_comment',
            'recipient_phone', 'recipient_name', 'recipient_name2',
            'update', 'comments', 'status'
        ]
        extra_kwargs = {
            'status': {'help_text': 'Все статусы коробок, включенных в заказ. '
                                    'Выводятся массивом с указанием статусов: '
                                    '["NEW", "ORDERED", ...]'}
        }


class OrderCreateSerializer(serializers.ModelSerializer):
    user = UserListRetrieveSerializer(read_only=True)
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'company',
            'logistic_tracking', 'client_tracking', 'client_name',
            'shipping_date', 'shipping_time', 'shipping_from',
            'shipping_car_type', 'shipping_method', 'recipient_order_num',
            'cargo_description', 'cargo_pallet', 'cargo_qty',
            'cargo_weight', 'cargo_price', 'recipient_id',
            'recipient_zip', 'recipient_city', 'recipient_email',
            'recipient_area', 'recipient_address', 'recipient_address_comment',
            'recipient_phone', 'recipient_name', 'recipient_name2',
            'update', 'comments', 'status'
        ]
        read_only_fields = [
            'id', 'user', 'company', 'logistic_tracking', 'update', 'status'
        ]
        extra_kwargs = {
            'status': {'help_text': 'Все статусы коробок, включенных в заказ. '
                                    'Выводятся массивом с указанием статусов: '
                                    '["NEW", "ORDERED", ...]'},
            'shipping_car_type': {'required': False},
        }

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['logistic_tracking'] = generate_logistic_tracking(self.context['request'].user.id)
        validated_data['company'] = self.context['request'].user.company
        order = super(OrderCreateSerializer, self).create(validated_data)
        Event.objects.create(
            status='NEW',
            order=order,
            user=self.context['request'].user,
        )
        return order

    def validate_client_tracking(self, value):
        if (Order.objects.filter(client_tracking=value,
                                 user__company_id=self.context['request'].user.company_id).exists()):
            raise ValidationError('The company already has an order with this number. Unable to add order.')
        return value


# TODO: сделать поля необязательными
class OrderUpdateSerializer(serializers.ModelSerializer):
    user = UserListRetrieveSerializer(read_only=True)
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'company',
            'logistic_tracking', 'client_tracking', 'client_name',
            'shipping_date', 'shipping_time', 'shipping_from',
            'shipping_car_type', 'shipping_method', 'recipient_order_num',
            'cargo_description', 'cargo_pallet', 'cargo_qty',
            'cargo_weight', 'cargo_price', 'recipient_id',
            'recipient_zip', 'recipient_city', 'recipient_email',
            'recipient_area', 'recipient_address', 'recipient_address_comment',
            'recipient_phone', 'recipient_name', 'recipient_name2',
            'update', 'comments', 'status'
        ]
        read_only_fields = [
            'id', 'user', 'company', 'logistic_tracking', 'update', 'status'
        ]
        extra_kwargs = {
            'status': {'help_text': 'Все статусы коробок, включенных в заказ. '
                                    'Выводятся массивом с указанием статусов: '
                                    '["NEW", "ORDERED", ...]'},
            'shipping_car_type': {'required': False},
            'client_tracking': {'required': False},
            'recipient_order_num': {'required': False},
        }

    def update(self, instance, validated_data):
        instance.update = timezone.now()
        return super(OrderUpdateSerializer, self).update(instance, validated_data)

    def validate_client_tracking(self, value):
        if (Order.objects.filter(client_tracking=value,
                                 user__company_id=self.context['request'].user.company_id).exists()):
            raise ValidationError('The company already has an order with this number. Unable to add order.')
        return value

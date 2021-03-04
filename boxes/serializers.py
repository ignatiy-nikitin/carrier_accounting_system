from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from boxes.models import Box
from orders.models import Order


class BoxListRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = ['id', 'order', 'client_code', 'code', 'width',
                  'height', 'length', 'weight',
                  'content_description', 'status', 'shipment']


class BoxCreateSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(source='order', queryset=Order.objects.all(), write_only=True,
                                                  required=True)

    class Meta:
        model = Box
        fields = ['id', 'order', 'order_id', 'client_code', 'code', 'width',
                  'height', 'length', 'weight',
                  'content_description', 'status', 'shipment']
        read_only_fields = ['id', 'status', 'order']

    def validate_order_id(self, value):
        if value.company != self.context['request'].user.company:
            raise ValidationError("An order with this id does not belong to the user's company.")
        return value


class BoxUpdateSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(source='order', queryset=Order.objects.all(), write_only=True,
                                                  required=False)

    class Meta:
        model = Box
        fields = ['id', 'order', 'order_id', 'client_code', 'code', 'width',
                  'height', 'length', 'weight',
                  'content_description', 'status', 'shipment']
        read_only_fields = ['id', 'status', 'order', 'shipment']
        extra_kwargs = {
            'client_code': {'required': False},
            'code': {'required': False},
        }

    def validate_order_id(self, value):
        if value.company != self.context['request'].user.company:
            raise ValidationError("An order with this id does not belong to the user's company.")
        return value

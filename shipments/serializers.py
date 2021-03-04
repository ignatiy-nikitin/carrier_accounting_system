from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from boxes.models import Box
from boxes.serializers import BoxListRetrieveSerializer
from events.models import Event
from shipments.models import Shipment
from users.serializers import UserListRetrieveSerializer


class ShipmentListRetrieveSerializer(serializers.ModelSerializer):
    author = UserListRetrieveSerializer()
    boxes = BoxListRetrieveSerializer(many=True)

    class Meta:
        model = Shipment
        fields = [
            'id', 'waybill_num', 'waybill_date',
            'comment', 'date_of_creation', 'author',
            'boxes'
        ]


class ShipmentCreateSerializer(serializers.ModelSerializer):
    boxes = BoxListRetrieveSerializer(many=True, read_only=True)
    boxes_ids = serializers.PrimaryKeyRelatedField(queryset=Box.objects.all(), source='boxes', write_only=True,
                                                   required=True, many=True)

    class Meta:
        model = Shipment
        fields = [
            'id', 'waybill_num', 'waybill_date',
            'comment', 'date_of_creation', 'author',
            'boxes', 'boxes_ids'
        ]
        read_only_fields = [
            'id', 'author', 'date_of_creation'
        ]
        extra_kwargs = {
            'boxes_ids': {'required': True},
        }

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        shipment = super(ShipmentCreateSerializer, self).create(validated_data)
        if 'boxes' in validated_data:
            for box in validated_data['boxes']:
                box.shipment = shipment
                box.status = Box.StatusChoices.SORTING
                box.save()
        Event.objects.create(
            status=Event.StatusChoices.READY_FOR_SHIPPING,
            comments=f'Номер транспортной накладной: {self.validated_data["waybill_num"]}',
            user=self.context['request'].user,
        )
        return shipment

    def validate_boxes_ids(self, value):
        for box in value:
            if not box.client_code:
                raise ValidationError(f'Box id = {box.id}. You cannot add a box without the given "client_code".')
        for box in value:
            if not box.order:
                raise ValidationError(f'Box id = {box.id}. You cannot add a box without the given "order".')
        for box in value:
            if (box.order.recipient_company.id != self.context['request'].user.company.id
                    and not self.context['request'].user.company.is_transport_company):
                raise ValidationError(f'Box with id = {box.id}. '
                                      f'Only those boxes can be added that belong to the company '
                                      f'to which the current user is attached')
        for box in value:
            if box.status not in (Box.StatusChoices.NEW, Box.StatusChoices.READY_FOR_SHIPPING):
                raise ValidationError(
                    f'Сan not add a box with id = {box.id}. Box status must be NEW or READY_FOR_SHIPPING')
        return value


class ShipmentUpdateSerializer(serializers.ModelSerializer):
    boxes = BoxListRetrieveSerializer(many=True, read_only=True)
    boxes_ids = serializers.PrimaryKeyRelatedField(queryset=Box.objects.all(), source='boxes', write_only=True,
                                                   required=False, many=True)

    class Meta:
        model = Shipment
        fields = [
            'id', 'waybill_num', 'waybill_date',
            'comment', 'date_of_creation', 'author',
            'boxes', 'boxes_ids'
        ]
        read_only_fields = [
            'id', 'author', 'date_of_creation'
        ]
        extra_kwargs = {
            'waybill_num': {'required': False},
            'waybill_date': {'required': False},
        }

    def update(self, instance, validated_data):
        validated_data['author'] = self.context['request'].user
        shipment = super(ShipmentUpdateSerializer, self).create(validated_data)
        if 'boxes' in validated_data:
            for box in validated_data['boxes']:
                box.shipment = shipment
                box.status = Box.StatusChoices.SORTING
                box.save()
        Event.objects.create(
            status=Event.StatusChoices.READY_FOR_SHIPPING,
            comments=f'Номер транспортной накладной: {self.validated_data["waybill_num"]}',
            user=self.context['request'].user,
        )
        return shipment

    def validate_boxes_ids(self, value):
        for box in value:
            if not box.client_code:
                raise ValidationError(f'Box id = {box.id}. You cannot add a box without the given "client_code".')
        for box in value:
            if not box.order:
                raise ValidationError(f'Box id = {box.id}. You cannot add a box without the given "order".')
        for box in value:
            if (box.order.recipient_company.id != self.context['request'].user.company.id
                    and not self.context['request'].user.company.is_transport_company):
                raise ValidationError(f'Box with id = {box.id}. '
                                      f'Only those boxes can be added that belong to the company '
                                      f'to which the current user is attached')
        for box in value:
            if box.status not in (Box.StatusChoices.NEW, Box.StatusChoices.READY_FOR_SHIPPING):
                raise ValidationError(
                    f'Сan not add a box with id = {box.id}. Box status must be NEW or READY_FOR_SHIPPING')
        return value

from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from shipments.models import Shipment
from shipments.serializers import ShipmentListRetrieveSerializer, ShipmentCreateSerializer
from users.permissions import IsUserNotBlocked


class ShipmentVewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.all()
    permission_classes = [IsAuthenticated, IsUserNotBlocked]

    def get_serializer_class(self):
        if self.action in ('create',):
            return ShipmentCreateSerializer
        elif self.action in ('list', 'retrieve'):
            return ShipmentListRetrieveSerializer

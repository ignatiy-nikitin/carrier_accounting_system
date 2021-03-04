from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from orders.models import Order
from orders.paginations import OrderPagination
from orders.serializers import OrderListRetrieveSerializer, OrderCreateSerializer, OrderUpdateSerializer
from users.permissions import IsUserNotBlocked


# @method_decorator(name='list', decorator=swagger_auto_schema(
#     responses={201: OrderCreateSerializer},
# ))
class OrderViewSet(viewsets.ModelViewSet):
    # queryset = Order.objects.all()
    pagination_class = OrderPagination
    permission_classes = [IsAuthenticated, IsUserNotBlocked]

    def get_queryset(self):
        return Order.objects.filter(company=self.request.user.company)

    def get_object(self):
        return get_object_or_404(Order, company=self.request.user.company, id=self.kwargs['pk'])

    def get_serializer_class(self):
        if self.action in ('create',):
            return OrderCreateSerializer
        elif self.action in ('list', 'retrieve'):
            return OrderListRetrieveSerializer
        elif self.action in ('update', 'partial_update'):
            return OrderUpdateSerializer

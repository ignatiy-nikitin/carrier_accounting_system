from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from boxes.models import Box
from boxes.serializers import BoxListRetrieveSerializer, BoxCreateSerializer, BoxUpdateSerializer
from users.permissions import IsUserNotBlocked



@method_decorator(name='list', decorator=swagger_auto_schema(
    #operation_description="description from swagger_auto_schema via method_decorator",
    responses={401: 'Authorization information is missing or invalid.'}
))
class BoxViewSet(viewsets.ModelViewSet):
    serializer_class = BoxListRetrieveSerializer
    permission_classes = [IsAuthenticated, IsUserNotBlocked]

    def get_queryset(self):
        return Box.objects.filter(order__company=self.request.user.company)

    def get_object(self):
        return get_object_or_404(Box, order__company=self.request.user.company, id=self.kwargs['pk'])

    def get_serializer_class(self):
        if self.action in ('create',):
            return BoxCreateSerializer
        elif self.action in ('list', 'retrieve'):
            return BoxListRetrieveSerializer
        elif self.action in ('update', 'partial_update'):
            return BoxUpdateSerializer

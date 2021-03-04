from rest_framework.routers import DefaultRouter

from shipments.views import ShipmentVewSet

shipment_router = DefaultRouter()
shipment_router.register('', ShipmentVewSet, basename='shipment')

urlpatterns = shipment_router.urls

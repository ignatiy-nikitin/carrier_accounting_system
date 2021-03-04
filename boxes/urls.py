from rest_framework.routers import DefaultRouter

from boxes.views import BoxViewSet

box_router = DefaultRouter()
box_router.register('', BoxViewSet, basename='box')

urlpatterns = box_router.urls

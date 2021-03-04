from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated

from users.serializers import UserCreateSerializer


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer


# class CustomAuthToken(ObtainAuthToken):
#     def aut
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

# from users.views import CurrentUserRetrieveUpdateAPIView, UserCreateAPIView
from users.views import UserCreateAPIView

urlpatterns = [
    path('auth/login/', obtain_auth_token),
    # path('auth/register/', UserCreateAPIView.as_view()),
    # path('current/', CurrentUserRetrieveUpdateAPIView.as_view()),
]

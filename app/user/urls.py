"""Url settings for the user API"""

from django.urls import path
from user.views import UserCreateView, TokenGenerateView, UserPersonalView

app_name = 'user'

urlpatterns = [
    path('create/', UserCreateView.as_view(), name='create'),
    path('token/', TokenGenerateView.as_view(), name='token'),
    path('me/', UserPersonalView.as_view(), name='me')
]

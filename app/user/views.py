"""Views for the user API"""
from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import UserCreateSerializer, TokenGenerateSerializer


class UserCreateView(CreateAPIView):
    """View: Creating user with a serializer"""
    serializer_class = UserCreateSerializer


class TokenGenerateView(ObtainAuthToken):
    """View: generating token"""
    serializer_class = TokenGenerateSerializer
    renderer_settings = api_settings.DEFAULT_RENDERER_CLASSES

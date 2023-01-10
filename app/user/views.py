"""Views for the user API"""
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import authentication, permissions
from user.serializers import UserCreateSerializer, TokenGenerateSerializer


class UserCreateView(CreateAPIView):
    """View: Creating user with a serializer"""
    serializer_class = UserCreateSerializer


class TokenGenerateView(ObtainAuthToken):
    """View: Generating token"""
    serializer_class = TokenGenerateSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserPersonalView(RetrieveUpdateAPIView):
    """View: Updating user credentials"""
    serializer_class = UserCreateSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Returning authenticated user"""
        return self.request.user

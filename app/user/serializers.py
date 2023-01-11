"""Serializers for the user API view"""

from rest_framework.serializers import ModelSerializer, Serializer, EmailField, CharField, ValidationError
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _


class UserCreateSerializer(ModelSerializer):
    """Serializer: Creating user"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        """Create user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update user"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user


class TokenGenerateSerializer(Serializer):
    """Serializer: Generating token"""
    email = EmailField()
    password = CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )

        if not user:
            _('Unable to authenticate')
            raise ValidationError

        attrs['user'] = user
        return attrs

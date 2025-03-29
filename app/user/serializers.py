"""
Serializers for the user API View.
"""
from typing import Dict, Any
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta: # type: ignore
        model = get_user_model()
        fields = ['email', 'password', 'name']
        # Can save it, but wont return for API
        extra_kwargs: Dict[str, Dict[str, Any]] = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data: Dict[str, Any]):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    # model instance is gonna update
    def update(self, instance: Any, validated_data: Dict[str, Any]):
        """Update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs: Any):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            # Headers and stuff
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code="authorization")

        attrs['user'] = user
        return attrs

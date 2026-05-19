from __future__ import annotations

from django.contrib.auth import authenticate as django_authenticate, get_user_model
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import AuthenticationFailed, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.users.serializers import UserRegistrationSerializer, UserSerializer

User = get_user_model()


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Accept email + password, return tokens + user data."""

    username_field = 'email'

    def validate(self, attrs: dict) -> dict:
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            raise AuthenticationFailed('No active account found with the given credentials.')

        # Django's ModelBackend authenticates by USERNAME_FIELD (username), not email
        authenticated = django_authenticate(
            request=self.context.get('request'),
            username=user.username,
            password=password,
        )
        if not authenticated or not authenticated.is_active:
            raise AuthenticationFailed('No active account found with the given credentials.')

        refresh = self.get_token(authenticated)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(authenticated, context=self.context).data,
        }


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class RegisterView(APIView):
    """Register a new user and return JWT tokens alongside user data."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user, context={'request': request}).data

        return Response(
            {
                'user': user_data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class LogoutView(APIView):
    """Blacklist the provided refresh token to log the user out."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)

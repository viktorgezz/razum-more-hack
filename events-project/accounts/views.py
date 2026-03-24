from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.serializers import LoginSerializer, RegisterSerializer, UserProfileSerializer


class RegisterView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    @extend_schema(
        tags=["Auth"],
        operation_id="auth_register",
        description="Регистрация нового пользователя с ролью и профилем.",
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserProfileSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    @extend_schema(
        tags=["Auth"],
        operation_id="auth_login",
        description="Логин пользователя и выдача JWT access/refresh токенов.",
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class RefreshView(TokenRefreshView):
    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        tags=["Auth"],
        operation_id="auth_refresh",
        description="Обновление access токена по refresh токену.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MeView(GenericAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        tags=["Auth"],
        operation_id="auth_me",
        description="Профиль текущего авторизованного пользователя.",
    )
    def get(self, request):
        return Response(self.get_serializer(request.user).data, status=status.HTTP_200_OK)

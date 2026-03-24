from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import RegisterSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        return token


@extend_schema(
    tags=['Authentication'],
    summary='Получить JWT-токены',
    description='Возвращает access и refresh по логину и паролю.',
)
class JWTTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    tags=['Authentication'],
    summary='Обновить access-токен',
    description='Возвращает новый access по действующему refresh-токену.',
)
class JWTTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(
    tags=['Authentication'],
    summary='Регистрация нового пользователя',
    description='Создаёт учётную запись участника и сразу возвращает JWT-токены.',
)
class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        # Генерируем токены, добавляем role и username (как в CustomTokenObtainPairSerializer)
        refresh = RefreshToken.for_user(user)
        refresh['role'] = user.role
        refresh['username'] = user.username

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_id": user.pk,
                "username": user.username,
                "role": user.role,
            },
            status=status.HTTP_201_CREATED,
        )

from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


@extend_schema(
    tags=['Аутентификация'],
    summary='Получить JWT-токены',
    description='Возвращает access и refresh токены по логину и паролю пользователя.',
)
class JWTTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(
    tags=['Аутентификация'],
    summary='Обновить access-токен',
    description='Возвращает новый access-токен по действующему refresh-токену.',
)
class JWTTokenRefreshView(TokenRefreshView):
    pass

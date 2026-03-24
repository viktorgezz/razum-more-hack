from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


@extend_schema(
    tags=['Authentication'],
    summary='Получить JWT-токены',
    description='Возвращает access и refresh по логину и паролю.',
)
class JWTTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(
    tags=['Authentication'],
    summary='Обновить access-токен',
    description='Возвращает новый access по действующему refresh-токену.',
)
class JWTTokenRefreshView(TokenRefreshView):
    pass

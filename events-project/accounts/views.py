from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


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

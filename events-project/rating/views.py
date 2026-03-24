from drf_spectacular.utils import OpenApiParameter, OpenApiExample, extend_schema
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PointWeight, RatingSnapshot
from .permissions import IsAdmin
from .serializers import PointWeightSerializer, RatingSnapshotSerializer
from .services import rebuild_leaderboard

ALLOWED_CATEGORIES = {'it', 'social', 'media'}
MAX_RESULTS = 100


@extend_schema(
    tags=['Рейтинговая система'],
    summary='Таблица лидеров',
    description='Возвращает топ-100 участников по рейтингу. Можно фильтровать по направлению.',
    parameters=[
        OpenApiParameter(
            name='category',
            description='Направление для фильтрации рейтинга',
            required=False,
            type=str,
            enum=['it', 'social', 'media'],
        ),
    ],
)
class LeaderboardView(ListAPIView):
    serializer_class = RatingSnapshotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = RatingSnapshot.objects.select_related('user')

        category = self.request.query_params.get('category')
        if category in ALLOWED_CATEGORIES:
            qs = qs.order_by(f'-rating_{category}')
        else:
            qs = qs.order_by('rank')

        return qs[:MAX_RESULTS]


@extend_schema(
    tags=['Рейтинговая система'],
    summary='Рейтинг пользователя',
    description='Возвращает детальный рейтинг участника по всем направлениям и его место в общем зачёте.',
)
class UserRatingView(RetrieveAPIView):
    serializer_class = RatingSnapshotSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user_id'
    queryset = RatingSnapshot.objects.select_related('user')


@extend_schema(
    tags=['Рейтинговая система'],
    summary='Список весов баллов',
    description='Коэффициенты для разных типов мероприятий, которые используются при расчёте рейтинга.',
)
class PointWeightListView(ListAPIView):
    serializer_class = PointWeightSerializer
    permission_classes = [IsAuthenticated]
    queryset = PointWeight.objects.all().order_by('event_type', 'id')


@extend_schema(
    tags=['Рейтинговая система'],
    summary='Изменить вес баллов',
    description='Только для администраторов. Позволяет настроить коэффициент для конкретного типа мероприятия.',
)
class PointWeightUpdateView(UpdateAPIView):
    serializer_class = PointWeightSerializer
    permission_classes = [IsAdmin]
    queryset = PointWeight.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema(
    tags=['Рейтинговая система'],
    summary='Принудительный пересчёт рейтинга',
    description='Только для администраторов. Пересчитывает рейтинг всех участников и обновляет места в таблице.',
)
class RebuildLeaderboardView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        rebuild_leaderboard()
        return Response({'status': 'ok', 'message': 'Рейтинг пересчитан'})

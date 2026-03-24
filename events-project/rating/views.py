from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView

from .models import PointWeight, RatingSnapshot
from .permissions import IsAdmin
from .serializers import PointWeightSerializer, RatingSnapshotSerializer
from .services import rebuild_leaderboard

ALLOWED_CATEGORIES = {'it', 'social', 'media'}
MAX_RESULTS = 100


@extend_schema(
    tags=['Ratings'],
    summary='Таблица лидеров',
    description='Топ-100 участников по рейтингу с опциональной фильтрацией по направлению.',
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
    tags=['Ratings'],
    summary='Рейтинг пользователя',
    description='Детальный рейтинг участника по направлениям и место в общем зачёте.',
)
class UserRatingView(RetrieveAPIView):
    serializer_class = RatingSnapshotSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user_id'
    queryset = RatingSnapshot.objects.select_related('user')


@extend_schema(
    tags=['Ratings'],
    summary='Список весов баллов',
    description='Коэффициенты по типам мероприятий, используемые при расчёте рейтинга.',
)
class PointWeightListView(ListAPIView):
    serializer_class = PointWeightSerializer
    permission_classes = [IsAuthenticated]
    queryset = PointWeight.objects.all().order_by('event_type', 'id')


@extend_schema(
    tags=['Ratings'],
    summary='Update point weight',
    description='Admin-only endpoint to update event type weight.',
)
class PointWeightUpdateView(UpdateAPIView):
    serializer_class = PointWeightSerializer
    permission_classes = [IsAdmin]
    queryset = PointWeight.objects.all()

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema(
    tags=['Ratings'],
    summary='Принудительный пересчёт рейтинга',
    description='Только для администраторов: пересчёт рейтингов и мест в таблице.',
    request=None,
    responses={
        200: inline_serializer(
            name='RebuildLeaderboardResponse',
            fields={
                'status': serializers.CharField(),
                'message': serializers.CharField(),
            },
        )
    },
)
class RebuildLeaderboardView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        rebuild_leaderboard()
        return Response({'status': 'ok', 'message': 'Рейтинг пересчитан'})

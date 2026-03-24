from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import DestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from events.models import Event, Participation, Prize
from organizers.models import OrganizerReview
from organizers.serializers import (
    OrganizerEventSerializer,
    OrganizerListSerializer,
    OrganizerProfileSerializer,
    OrganizerReviewCreateSerializer,
    OrganizerReviewSerializer,
)


@extend_schema(
    tags=['Профиль организатора'],
    summary='Список организаторов',
    description='Все верифицированные организаторы платформы с количеством проведённых мероприятий.',
)
class OrganizerListView(ListAPIView):
    serializer_class = OrganizerListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            User.objects
            .filter(role=User.Role.ORGANIZER)
            .annotate(events_count=Count('organized_events'))
            .order_by('id')
        )


class OrganizerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Профиль организатора'],
        summary='Публичный профиль организатора',
        description='Подробная страница организатора: статистика мероприятий, средний рейтинг доверия и типичные призы.',
        responses={200: OrganizerProfileSerializer},
    )
    def get(self, request, pk):
        organizer = get_object_or_404(User, pk=pk, role=User.Role.ORGANIZER)

        events_count = Event.objects.filter(organizer=organizer).count()

        review_stats = OrganizerReview.objects.filter(
            organizer=organizer,
        ).aggregate(
            avg_trust_score=Avg('score'),
            reviews_count=Count('id'),
        )

        frequent_prizes = list(
            Prize.objects
            .filter(event__organizer=organizer)
            .values('prize_type')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        data = {
            'id': organizer.id,
            'username': organizer.username,
            'first_name': organizer.first_name,
            'last_name': organizer.last_name,
            'avatar': organizer.avatar,
            'city': organizer.city,
            'is_verified': organizer.is_verified,
            'events_count': events_count,
            'avg_trust_score': review_stats['avg_trust_score'],
            'reviews_count': review_stats['reviews_count'],
            'frequent_prizes': frequent_prizes,
        }

        serializer = OrganizerProfileSerializer(data, context={'request': request})
        return Response(serializer.data)


@extend_schema(
    tags=['Профиль организатора'],
    summary='Мероприятия организатора',
    description='Список всех мероприятий, проведённых данным организатором.',
)
class OrganizerEventsView(ListAPIView):
    serializer_class = OrganizerEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(organizer_id=self.kwargs['pk']).order_by('-event_date')


@extend_schema(
    tags=['Профиль организатора'],
    summary='Отзывы об организаторе',
    description='Отзывы участников об организаторе с оценками от 1 до 5.',
)
class OrganizerReviewsListView(ListAPIView):
    serializer_class = OrganizerReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            OrganizerReview.objects
            .filter(organizer_id=self.kwargs['pk'])
            .select_related('reviewer', 'event')
        )


class OrganizerReviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Профиль организатора'],
        summary='Оставить отзыв',
        description='Только для участников. Можно оставить один отзыв на мероприятие при условии подтверждённого участия.',
        request=OrganizerReviewCreateSerializer,
        responses={201: OrganizerReviewSerializer},
    )
    def post(self, request, pk):
        if request.user.role != User.Role.PARTICIPANT:
            return Response(
                {'detail': 'Только участники могут оставлять отзывы.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = OrganizerReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event = serializer.validated_data['event']

        if event.organizer_id != pk:
            return Response(
                {'detail': 'Мероприятие не принадлежит этому организатору.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        has_confirmed = Participation.objects.filter(
            event=event,
            user=request.user,
            status=Participation.Status.CONFIRMED,
        ).exists()

        if not has_confirmed:
            return Response(
                {'detail': 'Вы не подтверждённый участник этого мероприятия.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if OrganizerReview.objects.filter(reviewer=request.user, event=event).exists():
            return Response(
                {'detail': 'Вы уже оставили отзыв на это мероприятие.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        review = OrganizerReview.objects.create(
            organizer_id=pk,
            reviewer=request.user,
            **serializer.validated_data,
        )

        return Response(
            OrganizerReviewSerializer(review).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=['Профиль организатора'],
    summary='Удалить свой отзыв',
    description='Участник может удалить только свой собственный отзыв.',
)
class OrganizerReviewDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        review = get_object_or_404(
            OrganizerReview,
            pk=self.kwargs['review_id'],
            organizer_id=self.kwargs['pk'],
        )
        if review.reviewer != self.request.user:
            self.permission_denied(self.request, message='Можно удалить только свой отзыв.')
        return review

from django.contrib.auth import get_user_model

from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view, inline_serializer
from rest_framework import exceptions, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import serializers

from events.filters import filter_events
from events.models import Event, Participation, Prize
from events.serializers import EventSerializer, ParticipationSerializer, PrizeSerializer
from events.services import checkin_for_event, confirm_participation, register_for_event

User = get_user_model()


EVENT_LIST_PARAMETERS = [
    OpenApiParameter(name="category", description="Слаг направления", required=False, type=str),
    OpenApiParameter(name="status", description="Статус мероприятия", required=False, type=str),
    OpenApiParameter(name="event_type", description="Тип мероприятия", required=False, type=str),
    OpenApiParameter(name="organizer_id", description="ID организатора", required=False, type=int),
    OpenApiParameter(name="date_from", description="Начало периода (YYYY-MM-DD)", required=False, type=str),
    OpenApiParameter(name="date_to", description="Конец периода (YYYY-MM-DD)", required=False, type=str),
    OpenApiParameter(name="ordering", description="Поле сортировки", required=False, type=str),
]


@extend_schema_view(
    list=extend_schema(
        tags=["Events"],
        summary="Список мероприятий",
        description="Лента мероприятий с пагинацией, фильтрацией и сортировкой.",
        parameters=EVENT_LIST_PARAMETERS,
    ),
    create=extend_schema(
        tags=["Events"],
        summary="Создать мероприятие",
        description="Доступно организатору или администратору. Организатором записи становится текущий пользователь.",
    ),
    retrieve=extend_schema(
        tags=["Events"],
        summary="Карточка мероприятия",
        description="Подробная информация о мероприятии и связанных призах.",
    ),
    update=extend_schema(
        tags=["Events"],
        summary="Полная замена мероприятия",
        description="Полное обновление карточки мероприятия его организатором или администратором.",
    ),
    partial_update=extend_schema(
        tags=["Events"],
        summary="Частичное обновление мероприятия",
        description="Частичное обновление карточки мероприятия его организатором или администратором.",
    ),
    destroy=extend_schema(
        tags=["Events"],
        summary="Удалить мероприятие",
        description="Удаление мероприятия его организатором или администратором.",
    ),
)
class EventViewSet(viewsets.ModelViewSet):
    """Мероприятия: CRUD, регистрация, чекин и подтверждение участия."""

    queryset = Event.objects.select_related("category", "organizer").prefetch_related("prizes")
    serializer_class = EventSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (OrderingFilter,)
    ordering_fields = ("event_date", "created_at", "base_points", "difficulty_coef", "name")
    ordering = ("-event_date",)

    def get_queryset(self):
        queryset = super().get_queryset()
        return filter_events(queryset, self.request.query_params)

    def _ensure_organizer_access(self, event=None):
        user = self.request.user
        if not user.is_authenticated:
            raise exceptions.NotAuthenticated()

        is_admin = user.is_staff or user.role == User.Role.ADMIN
        is_organizer = user.role == User.Role.ORGANIZER
        if not (is_admin or is_organizer):
            raise exceptions.PermissionDenied("Only organizers or admins can manage events.")

        if event is not None and not is_admin and event.organizer_id != user.id:
            raise exceptions.PermissionDenied("Only the event organizer can manage this event.")

    def _ensure_participant_access(self):
        user = self.request.user
        if not user.is_authenticated:
            raise exceptions.NotAuthenticated()
        if user.role != User.Role.PARTICIPANT:
            raise exceptions.PermissionDenied("Only participants can register for events.")

    def perform_create(self, serializer):
        self._ensure_organizer_access()
        serializer.save(organizer=self.request.user)

    def perform_update(self, serializer):
        self._ensure_organizer_access(self.get_object())
        serializer.save()

    def perform_destroy(self, instance):
        self._ensure_organizer_access(instance)
        instance.delete()

    @extend_schema(
        tags=["Events"],
        summary="Записаться на мероприятие",
        description="Создаёт заявку на участие и QR-токен для последующего чекина.",
        responses={200: ParticipationSerializer, 201: ParticipationSerializer},
    )
    @action(methods=["post"], detail=True, permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        self._ensure_participant_access()
        event = self.get_object()
        participation, created = register_for_event(event, request.user)
        data = ParticipationSerializer(participation).data
        data["created"] = created
        return Response(data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @extend_schema(
        tags=["Events"],
        summary="Отметиться по QR",
        description="Подтверждает присутствие участника на мероприятии по QR-токену.",
        request=inline_serializer(
            name="EventCheckInRequest",
            fields={"qr_token": serializers.CharField()},
        ),
        responses={200: ParticipationSerializer},
    )
    @action(methods=["post"], detail=True, permission_classes=[IsAuthenticated])
    def checkin(self, request, pk=None):
        self._ensure_participant_access()
        qr_token = request.data.get("qr_token")
        if not qr_token:
            return Response(
                {"detail": "qr_token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        event = self.get_object()
        participation = checkin_for_event(event, request.user, qr_token=qr_token)
        return Response(ParticipationSerializer(participation).data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Events"],
        summary="Подтвердить участие",
        description="Организатор или администратор подтверждает участие пользователя и начисляет баллы.",
        parameters=[
            OpenApiParameter(
                name="user_id",
                location=OpenApiParameter.PATH,
                required=True,
                type=int,
                description="ID участника для подтверждения",
            )
        ],
        responses={200: ParticipationSerializer},
    )
    @action(
        methods=["post"],
        detail=True,
        url_path=r"confirm/(?P<user_id>[^/.]+)",
        permission_classes=[IsAuthenticated],
    )
    def confirm(self, request, pk=None, user_id=None):
        event = self.get_object()
        self._ensure_organizer_access(event)

        try:
            participant = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        participation = confirm_participation(event, participant)
        return Response(ParticipationSerializer(participation).data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Events"],
        summary="Список участников",
        description="Регистрации на мероприятие. Доступно организатору события и администратору.",
        responses={200: ParticipationSerializer(many=True)},
    )
    @action(methods=["get"], detail=True, permission_classes=[IsAuthenticated])
    def participants(self, request, pk=None):
        event = self.get_object()
        self._ensure_organizer_access(event)
        queryset = event.participations.select_related("user").order_by("-created_at")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ParticipationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(ParticipationSerializer(queryset, many=True).data)

    @extend_schema(
        tags=["Events"],
        summary="Список или создание призов",
        description="GET — призы мероприятия. POST — добавление приза организатором или администратором.",
        request=PrizeSerializer,
        responses={200: PrizeSerializer(many=True), 201: PrizeSerializer},
    )
    @extend_schema(
        tags=["Events"],
        summary="Моё участие в мероприятии",
        description="Возвращает участие текущего пользователя в мероприятии, включая QR-токен.",
        responses={200: ParticipationSerializer, 404: None},
    )
    @action(methods=["get"], detail=True, url_path="my-participation", permission_classes=[IsAuthenticated])
    def my_participation(self, request, pk=None):
        event = self.get_object()
        try:
            participation = event.participations.get(user=request.user)
            return Response(ParticipationSerializer(participation).data)
        except Participation.DoesNotExist:
            return Response({"detail": "Вы не зарегистрированы на это мероприятие."}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        tags=["Events"],
        summary="Чекин по QR (организатор)",
        description="Организатор сканирует QR-код участника и отмечает его присутствие.",
        request=inline_serializer(
            name="OrganizerCheckinRequest",
            fields={"qr_token": serializers.CharField()},
        ),
        responses={200: ParticipationSerializer},
    )
    @action(methods=["post"], detail=True, url_path="organizer-checkin", permission_classes=[IsAuthenticated])
    def organizer_checkin(self, request, pk=None):
        event = self.get_object()
        self._ensure_organizer_access(event)
        qr_token = request.data.get("qr_token", "").strip()
        if not qr_token:
            return Response({"detail": "qr_token обязателен."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            participation = Participation.objects.get(event=event, qr_token=qr_token)
        except Participation.DoesNotExist:
            return Response({"detail": "Неверный QR-код."}, status=status.HTTP_400_BAD_REQUEST)
        if participation.status in (Participation.Status.CONFIRMED, Participation.Status.REJECTED):
            return Response({"detail": "Участник уже подтверждён или отклонён."}, status=status.HTTP_400_BAD_REQUEST)
        participation.mark_checked_in()
        participation.save(update_fields=["status", "checked_in_at"])
        return Response(ParticipationSerializer(participation).data, status=status.HTTP_200_OK)

    @action(methods=["get", "post"], detail=True, permission_classes=[IsAuthenticatedOrReadOnly])
    def prizes(self, request, pk=None):
        event = self.get_object()
        if request.method == "GET":
            queryset = event.prizes.all().order_by("name")
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = PrizeSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            return Response(PrizeSerializer(queryset, many=True).data)

        self._ensure_organizer_access(event)
        serializer = PrizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(event=event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Events"],
    summary="Получить приз",
    description="Детальная информация о призе и связанном мероприятии.",
)
class PrizeViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Prize.objects.select_related("event")
    serializer_class = PrizeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

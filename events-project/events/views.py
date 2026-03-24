from django.contrib.auth import get_user_model

from rest_framework import exceptions, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from accounts.permissions import IsParticipant
from events.filters import filter_events
from events.models import Event, Participation, Prize
from events.serializers import EventSerializer, ParticipationSerializer, PrizeSerializer
from events.services import checkin_for_event, confirm_participation, register_for_event

User = get_user_model()


class ParticipantsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ParticipantEventsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


_PARTICIPANT_EVENT_ORDERING = {
    "event_date": "event_date",
    "-event_date": "-event_date",
    "created_at": "created_at",
    "-created_at": "-created_at",
    "name": "name",
    "-name": "-name",
}


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

    def _participant_event_ordering(self, request, default: str = "event_date") -> str:
        raw = request.query_params.get("ordering", default)
        return _PARTICIPANT_EVENT_ORDERING.get(raw, _PARTICIPANT_EVENT_ORDERING.get(default, "event_date"))

    @action(
        detail=False,
        methods=["get"],
        url_path="participant/catalog",
        permission_classes=[IsAuthenticated, IsParticipant],
    )
    @swagger_auto_schema(
        operation_description=(
            "Каталог мероприятий для участника: только опубликованные / идущие / завершённые. "
            "Пагинация и сортировка по времени мероприятия (`event_date`)."
        ),
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, description="Номер страницы", type=openapi.TYPE_INTEGER),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Размер страницы (до 100)",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Сортировка: event_date, -event_date (по умолчанию event_date — сначала ближайшие)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter("category", openapi.IN_QUERY, description="slug категории", type=openapi.TYPE_STRING),
            openapi.Parameter("event_type", openapi.IN_QUERY, description="тип мероприятия", type=openapi.TYPE_STRING),
            openapi.Parameter("organizer_id", openapi.IN_QUERY, description="ID организатора", type=openapi.TYPE_INTEGER),
            openapi.Parameter("date_from", openapi.IN_QUERY, description="дата события с (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter("date_to", openapi.IN_QUERY, description="дата события по (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
    )
    def participant_catalog(self, request):
        queryset = (
            Event.objects.filter(
                status__in=[
                    Event.Status.PUBLISHED,
                    Event.Status.ONGOING,
                    Event.Status.COMPLETED,
                ]
            )
            .select_related("category", "organizer")
            .prefetch_related("prizes")
        )
        queryset = filter_events(queryset, request.query_params)
        queryset = queryset.order_by(self._participant_event_ordering(request, default="event_date"))

        paginator = ParticipantEventsPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            return paginator.get_paginated_response(EventSerializer(page, many=True).data)
        return Response(EventSerializer(queryset, many=True).data)

    @action(
        detail=False,
        methods=["get"],
        url_path="participant/my",
        permission_classes=[IsAuthenticated, IsParticipant],
    )
    @swagger_auto_schema(
        operation_description=(
            "Мероприятия, на которые зарегистрирован текущий участник. "
            "Пагинация и сортировка по времени мероприятия (`event_date`)."
        ),
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, description="Номер страницы", type=openapi.TYPE_INTEGER),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Размер страницы (до 100)",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Сортировка: event_date, -event_date (по умолчанию event_date)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter("category", openapi.IN_QUERY, description="slug категории", type=openapi.TYPE_STRING),
            openapi.Parameter("event_type", openapi.IN_QUERY, description="тип мероприятия", type=openapi.TYPE_STRING),
            openapi.Parameter("date_from", openapi.IN_QUERY, description="дата события с (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter("date_to", openapi.IN_QUERY, description="дата события по (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
    )
    def participant_my_events(self, request):
        queryset = (
            Event.objects.filter(participations__user=request.user)
            .select_related("category", "organizer")
            .prefetch_related("prizes")
            .distinct()
        )
        queryset = filter_events(queryset, request.query_params)
        queryset = queryset.order_by(self._participant_event_ordering(request, default="event_date"))

        paginator = ParticipantEventsPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            return paginator.get_paginated_response(EventSerializer(page, many=True).data)
        return Response(EventSerializer(queryset, many=True).data)

    @swagger_auto_schema(operation_description="Получить список мероприятий (с пагинацией, фильтрацией и сортировкой).")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Создать новое мероприятие.")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Получить карточку мероприятия по ID.")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Частично обновить мероприятие.")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Удалить мероприятие.")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    def perform_update(self, serializer):
        event = self.get_object()
        user = self.request.user
        if not user.is_staff and event.organizer_id != user.id:
            raise exceptions.PermissionDenied("Only organizer can update this event.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not user.is_staff and instance.organizer_id != user.id:
            raise exceptions.PermissionDenied("Only organizer can delete this event.")
        instance.delete()

    @action(methods=["post"], detail=True, permission_classes=[IsAuthenticated])
    @swagger_auto_schema(operation_description="Записаться на мероприятие. Возвращает запись участия и признак created.")
    def register(self, request, pk=None):
        event = self.get_object()
        participation, created = register_for_event(event, request.user)
        data = ParticipationSerializer(participation).data
        data["created"] = created
        return Response(data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(methods=["post"], detail=True, permission_classes=[IsAuthenticated])
    @swagger_auto_schema(operation_description="Отметиться на мероприятии по QR-токену.")
    def checkin(self, request, pk=None):
        qr_token = request.data.get("qr_token")
        if not qr_token:
            return Response(
                {"detail": "qr_token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        event = self.get_object()
        participation = checkin_for_event(event, request.user, qr_token=qr_token)
        return Response(ParticipationSerializer(participation).data, status=status.HTTP_200_OK)

    @action(
        methods=["post"],
        detail=True,
        url_path=r"confirm/(?P<user_id>[^/.]+)",
        permission_classes=[IsAuthenticated],
    )
    @swagger_auto_schema(operation_description="Подтвердить участие пользователя организатором.")
    def confirm(self, request, pk=None, user_id=None):
        event = self.get_object()
        if not request.user.is_staff and event.organizer_id != request.user.id:
            return Response(
                {"detail": "Only event organizer can confirm participation."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            participant = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        participation = confirm_participation(event, participant)
        return Response(ParticipationSerializer(participation).data, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=True, permission_classes=[IsAuthenticated])
    @swagger_auto_schema(
        operation_description="Получить список участников мероприятия (с пагинацией и фильтром по дате события).",
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, description="Номер страницы", type=openapi.TYPE_INTEGER),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Размер страницы (до 100)",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "event_date_from",
                openapi.IN_QUERY,
                description="Фильтр по дате события: от (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "event_date_to",
                openapi.IN_QUERY,
                description="Фильтр по дате события: до (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Сортировка: created_at, -created_at, event_date, -event_date",
                type=openapi.TYPE_STRING,
            ),
        ],
    )
    def participants(self, request, pk=None):
        event = self.get_object()
        if not request.user.is_staff and event.organizer_id != request.user.id:
            return Response(
                {"detail": "Only event organizer can view participants."},
                status=status.HTTP_403_FORBIDDEN,
            )

        date_from = request.query_params.get("event_date_from")
        date_to = request.query_params.get("event_date_to")
        if date_from and str(event.event_date.date()) < date_from:
            return Response({"count": 0, "next": None, "previous": None, "results": []})
        if date_to and str(event.event_date.date()) > date_to:
            return Response({"count": 0, "next": None, "previous": None, "results": []})

        ordering = request.query_params.get("ordering", "-created_at")
        allowed_ordering = {
            "created_at": "created_at",
            "-created_at": "-created_at",
            "event_date": "event__event_date",
            "-event_date": "-event__event_date",
        }
        queryset = event.participations.select_related("user", "event").order_by(
            allowed_ordering.get(ordering, "-created_at")
        )

        paginator = ParticipantsPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = ParticipationSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        return Response(ParticipationSerializer(queryset, many=True).data)

    @action(methods=["get", "post"], detail=True, permission_classes=[IsAuthenticatedOrReadOnly])
    @swagger_auto_schema(operation_description="Получить список призов мероприятия или добавить новый приз.")
    def prizes(self, request, pk=None):
        event = self.get_object()
        if request.method == "GET":
            queryset = event.prizes.all().order_by("name")
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = PrizeSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            return Response(PrizeSerializer(queryset, many=True).data)

        if not request.user.is_staff and event.organizer_id != request.user.id:
            return Response(
                {"detail": "Only event organizer can add prizes."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = PrizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(event=event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PrizeViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Prize.objects.select_related("event")
    serializer_class = PrizeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

from django.contrib.auth import get_user_model

from rest_framework import exceptions, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from events.filters import filter_events
from events.models import Event, Participation, Prize
from events.serializers import EventSerializer, ParticipationSerializer, PrizeSerializer
from events.services import checkin_for_event, confirm_participation, register_for_event

User = get_user_model()


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
    @swagger_auto_schema(operation_description="Получить список участников мероприятия (с пагинацией).")
    def participants(self, request, pk=None):
        event = self.get_object()
        if not request.user.is_staff and event.organizer_id != request.user.id:
            return Response(
                {"detail": "Only event organizer can view participants."},
                status=status.HTTP_403_FORBIDDEN,
            )
        queryset = event.participations.select_related("user").order_by("-created_at")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ParticipationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
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

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response

from admin_panel.serializers import (
    OrganizerModerationSerializer,
    PendingOrganizerSerializer,
    PointWeightPatchSerializer,
    PointWeightReadSerializer,
)
from rating.models import PointWeight

User = get_user_model()


class IsAdminPanelAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_staff or getattr(user, "role", None) == "ADMIN")
        )


@extend_schema(
    tags=["Admin Panel"],
    summary="Кандидаты в организаторы",
    description="Пользователи, ожидающие модерации организатора.",
)
class PendingOrganizerListView(ListAPIView):
    permission_classes = (IsAdminPanelAccess,)
    serializer_class = PendingOrganizerSerializer
    queryset = User.objects.filter(is_staff=False, is_superuser=False).order_by("id")


@extend_schema(
    tags=["Admin Panel"],
    summary="Одобрить организатора",
    description="Выдаёт права организатора (is_staff=True и роль ORGANIZER).",
    responses={200: OrganizerModerationSerializer},
)
class OrganizerApproveView(GenericAPIView):
    permission_classes = (IsAdminPanelAccess,)
    serializer_class = OrganizerModerationSerializer

    def post(self, request, user_id: int):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"detail": "Пользователь не найден."}, status=404)
        user.is_staff = True
        user.role = User.Role.ORGANIZER
        user.save(update_fields=["is_staff", "role"])
        return Response(
            {
                "detail": "Пользователь одобрен как организатор.",
                "user_id": user.id,
                "is_staff": user.is_staff,
                "role": user.role,
                "is_active": user.is_active,
            }
        )


@extend_schema(
    tags=["Admin Panel"],
    summary="Отклонить организатора",
    description="Снимает права организатора (is_staff=False, при необходимости роль PARTICIPANT).",
    responses={200: OrganizerModerationSerializer},
)
class OrganizerRejectView(GenericAPIView):
    permission_classes = (IsAdminPanelAccess,)
    serializer_class = OrganizerModerationSerializer

    def post(self, request, user_id: int):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"detail": "Пользователь не найден."}, status=404)
        user.is_staff = False
        if user.role == User.Role.ORGANIZER:
            user.role = User.Role.PARTICIPANT
            user.save(update_fields=["is_staff", "role"])
        else:
            user.save(update_fields=["is_staff"])
        return Response(
            {
                "detail": "Заявка организатора отклонена.",
                "user_id": user.id,
                "is_staff": user.is_staff,
                "role": user.role,
                "is_active": user.is_active,
            }
        )


@extend_schema(
    tags=["Admin Panel"],
    summary="Список весов баллов",
    description="Текущие веса по типам мероприятий и категориям.",
)
class PointWeightListView(ListAPIView):
    permission_classes = (IsAdminPanelAccess,)
    serializer_class = PointWeightReadSerializer
    queryset = PointWeight.objects.select_related("category", "updated_by").all()
    filter_backends = (OrderingFilter,)
    ordering_fields = ("event_type", "weight", "updated_at")
    ordering = ("event_type", "category_id")


@extend_schema(
    tags=["Admin Panel"],
    summary="Обновить вес баллов",
    description="Обновляет PointWeight и проставляет updated_by текущим администратором.",
    request=PointWeightPatchSerializer,
    responses={200: PointWeightReadSerializer},
)
class PointWeightDetailView(GenericAPIView):
    permission_classes = (IsAdminPanelAccess,)
    serializer_class = PointWeightPatchSerializer

    def patch(self, request, weight_id: int):
        point_weight = PointWeight.objects.filter(id=weight_id).first()
        if not point_weight:
            return Response({"detail": "Настройка веса не найдена."}, status=404)
        serializer = self.get_serializer(point_weight, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        point_weight = serializer.save(updated_by=request.user)
        return Response(PointWeightReadSerializer(point_weight).data)

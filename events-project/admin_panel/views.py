from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
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
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class PendingOrganizerListView(ListAPIView):
    permission_classes = (IsAdminPanelAccess,)
    serializer_class = PendingOrganizerSerializer
    queryset = User.objects.filter(is_staff=False, is_superuser=False).order_by("id")

    @swagger_auto_schema(operation_description="Получить список пользователей на модерацию организаторов.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class OrganizerApproveView(GenericAPIView):
    permission_classes = (IsAdminPanelAccess,)
    serializer_class = OrganizerModerationSerializer

    @swagger_auto_schema(operation_description="Одобрить организатора (fallback: установить is_staff=True).")
    def post(self, request, user_id: int):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"detail": "Пользователь не найден."}, status=404)
        user.is_staff = True
        user.save(update_fields=["is_staff"])
        return Response(
            {
                "detail": "Пользователь одобрен как организатор.",
                "user_id": user.id,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
            }
        )


class OrganizerRejectView(GenericAPIView):
    permission_classes = (IsAdminPanelAccess,)
    serializer_class = OrganizerModerationSerializer

    @swagger_auto_schema(operation_description="Отклонить организатора (fallback: установить is_staff=False).")
    def post(self, request, user_id: int):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"detail": "Пользователь не найден."}, status=404)
        user.is_staff = False
        user.save(update_fields=["is_staff"])
        return Response(
            {
                "detail": "Заявка организатора отклонена.",
                "user_id": user.id,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
            }
        )


class PointWeightListView(ListAPIView):
    permission_classes = (IsAdminPanelAccess,)
    serializer_class = PointWeightReadSerializer
    queryset = PointWeight.objects.select_related("category", "updated_by").all()
    filter_backends = (OrderingFilter,)
    ordering_fields = ("event_type", "weight", "updated_at")
    ordering = ("event_type", "category_id")

    @swagger_auto_schema(operation_description="Список весов баллов для типов мероприятий.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PointWeightDetailView(GenericAPIView):
    permission_classes = (IsAdminPanelAccess,)
    serializer_class = PointWeightPatchSerializer

    @swagger_auto_schema(operation_description="Обновить вес баллов по записи PointWeight.")
    def patch(self, request, weight_id: int):
        point_weight = PointWeight.objects.filter(id=weight_id).first()
        if not point_weight:
            return Response({"detail": "Настройка веса не найдена."}, status=404)
        serializer = self.get_serializer(point_weight, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        point_weight = serializer.save(updated_by=request.user)
        return Response(PointWeightReadSerializer(point_weight).data)

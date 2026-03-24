from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from events.models import Participation
from inspector.filters import apply_candidate_filters
from inspector.serializers import CandidateListSerializer
from inspector.services import generate_candidate_pdf

User = get_user_model()


class IsInspectorAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in {User.Role.ADMIN, User.Role.OBSERVER}
        )


def candidates_queryset():
    return (
        User.objects.filter(role=User.Role.PARTICIPANT).annotate(
            events_count=Count("participations", distinct=True),
            confirmed_count=Count(
                "participations",
                filter=Q(participations__status=Participation.Status.CONFIRMED),
                distinct=True,
            ),
            total_points=Coalesce(Sum("participations__points_awarded"), Value(0)),
            avg_points=Coalesce(Avg("participations__points_awarded"), Value(0.0)),
        )
        .filter(events_count__gt=0)
        .distinct()
    )


@extend_schema(
    tags=["Инспектор кадрового резерва"],
    summary="Список кандидатов",
    description="Список участников с расширенной фильтрацией для кадровой службы.",
    parameters=[
        OpenApiParameter(name="min_events", required=False, type=int, description="Минимум мероприятий"),
        OpenApiParameter(name="max_events", required=False, type=int, description="Максимум мероприятий"),
        OpenApiParameter(name="min_avg_points", required=False, type=float, description="Минимальный средний балл"),
        OpenApiParameter(name="max_avg_points", required=False, type=float, description="Максимальный средний балл"),
        OpenApiParameter(
            name="ordering",
            required=False,
            type=str,
            description="Сортировка: total_points, avg_points, events_count, date_joined и варианты с '-'",
        ),
    ],
    responses={200: CandidateListSerializer(many=True)},
)
class CandidateListView(GenericAPIView):
    permission_classes = (IsAuthenticated, IsInspectorAccess)
    serializer_class = CandidateListSerializer

    def get(self, request):
        queryset = apply_candidate_filters(candidates_queryset(), request.query_params)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(
    tags=["Инспектор кадрового резерва"],
    summary="PDF-отчёт по кандидату",
    description="Скачивание PDF-отчёта с краткой статистикой и последними участиями кандидата.",
    responses={
        200: OpenApiResponse(description="PDF-файл отчёта"),
        404: OpenApiResponse(description="Кандидат не найден"),
    },
)
class CandidateReportView(GenericAPIView):
    permission_classes = (IsAuthenticated, IsInspectorAccess)

    def get(self, request, user_id: int):
        candidate = candidates_queryset().filter(id=user_id).first()
        if not candidate:
            return Response({"detail": "Кандидат не найден."}, status=status.HTTP_404_NOT_FOUND)

        participations = (
            Participation.objects.filter(user_id=user_id)
            .select_related("event")
            .order_by("-created_at")
        )
        stats = {
            "events_count": candidate.events_count,
            "confirmed_count": candidate.confirmed_count,
            "total_points": candidate.total_points,
            "avg_points": round(float(candidate.avg_points), 2),
        }
        pdf_bytes = generate_candidate_pdf(candidate, stats, participations)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="candidate_{user_id}_report.pdf"'
        return response

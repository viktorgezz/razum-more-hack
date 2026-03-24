from django.contrib.auth import get_user_model
from django.db.models import Avg, Case, Count, IntegerField, Sum, Value, When
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from events.models import Participation
from inspector.filters import apply_candidate_filters
from inspector.serializers import CandidateListSerializer, CandidateReportMetaSerializer
from inspector.services import generate_candidate_pdf

User = get_user_model()


class IsInspectorAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        # Fallback policy until role-based accounts is implemented.
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


def candidates_queryset():
    return (
        User.objects.annotate(
            events_count=Count("participations", distinct=True),
            confirmed_count=Count(
                Case(
                    When(participations__status=Participation.Status.CONFIRMED, then=1),
                    output_field=IntegerField(),
                )
            ),
            total_points=Coalesce(Sum("participations__points_awarded"), Value(0)),
            avg_points=Coalesce(Avg("participations__points_awarded"), Value(0.0)),
        )
        .filter(events_count__gt=0)
        .distinct()
    )


class CandidateListView(GenericAPIView):
    permission_classes = (IsInspectorAccess,)
    serializer_class = CandidateListSerializer

    @swagger_auto_schema(operation_description="Список кандидатов с фильтрацией и сортировкой для кадрового инспектора.")
    def get(self, request):
        queryset = apply_candidate_filters(candidates_queryset(), request.query_params)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CandidateReportView(GenericAPIView):
    permission_classes = (IsInspectorAccess,)
    serializer_class = CandidateReportMetaSerializer

    @swagger_auto_schema(operation_description="Скачать PDF-отчет по кандидату.")
    def get(self, request, user_id: int):
        candidate = candidates_queryset().filter(id=user_id).first()
        if not candidate:
            return Response({"detail": "Кандидат не найден."}, status=404)

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

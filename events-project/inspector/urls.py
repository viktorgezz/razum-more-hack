from django.urls import path

from inspector.views import CandidateListView, CandidateReportView

urlpatterns = [
    path("candidates/", CandidateListView.as_view(), name="inspector-candidates"),
    path("candidates/<int:user_id>/report/", CandidateReportView.as_view(), name="inspector-candidate-report"),
]

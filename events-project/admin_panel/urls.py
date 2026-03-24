from django.urls import path

from admin_panel.views import (
    OrganizerApproveView,
    OrganizerRejectView,
    PendingOrganizerListView,
    PointWeightDetailView,
    PointWeightListView,
)

urlpatterns = [
    path("organizers/pending/", PendingOrganizerListView.as_view(), name="admin-pending-organizers"),
    path("organizers/<int:user_id>/approve/", OrganizerApproveView.as_view(), name="admin-approve-organizer"),
    path("organizers/<int:user_id>/reject/", OrganizerRejectView.as_view(), name="admin-reject-organizer"),
    path("point-weights/", PointWeightListView.as_view(), name="admin-point-weights"),
    path("point-weights/<int:weight_id>/", PointWeightDetailView.as_view(), name="admin-point-weight-detail"),
]

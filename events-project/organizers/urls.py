from django.urls import path

from .views import (
    OrganizerEventsView,
    OrganizerListView,
    OrganizerProfileView,
    OrganizerReviewCreateView,
    OrganizerReviewDeleteView,
    OrganizerReviewsListView,
)

app_name = 'organizers'

urlpatterns = [
    path('', OrganizerListView.as_view(), name='list'),
    path('<int:pk>/', OrganizerProfileView.as_view(), name='profile'),
    path('<int:pk>/events/', OrganizerEventsView.as_view(), name='events'),
    path('<int:pk>/reviews/', OrganizerReviewsListView.as_view(), name='reviews'),
    path('<int:pk>/reviews/create/', OrganizerReviewCreateView.as_view(), name='review-create'),
    path('<int:pk>/reviews/<int:review_id>/', OrganizerReviewDeleteView.as_view(), name='review-delete'),
]

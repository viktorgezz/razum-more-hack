from django.urls import path

from .views import (
    LeaderboardView,
    PointWeightListView,
    PointWeightUpdateView,
    RebuildLeaderboardView,
    UserRatingView,
)

app_name = 'rating'

urlpatterns = [
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('user/<int:user_id>/', UserRatingView.as_view(), name='user-rating'),
    path('point-weights/', PointWeightListView.as_view(), name='point-weight-list'),
    path('point-weights/<int:pk>/', PointWeightUpdateView.as_view(), name='point-weight-update'),
    path('rebuild/', RebuildLeaderboardView.as_view(), name='rebuild'),
]

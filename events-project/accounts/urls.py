from django.urls import path

from accounts.views import JWTTokenObtainPairView, JWTTokenRefreshView, MeView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", JWTTokenObtainPairView.as_view(), name="auth-login"),
    path("refresh/", JWTTokenRefreshView.as_view(), name="auth-refresh"),
    path("me/", MeView.as_view(), name="auth-me"),
]

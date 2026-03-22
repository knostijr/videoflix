"""URL configuration for the users app."""

from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path(
        'activate/<str:uidb64>/<str:token>/',
        views.ActivateAccountView.as_view(),
        name='activate',
    ),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path(
        'token/refresh/',
        views.TokenRefreshView.as_view(),
        name='token-refresh',
    ),
    path(
        'password_reset/',
        views.PasswordResetView.as_view(),
        name='password-reset',
    ),
    path(
        'password_confirm/<str:uidb64>/<str:token>/',
        views.PasswordConfirmView.as_view(),
        name='password-confirm',
    ),
]
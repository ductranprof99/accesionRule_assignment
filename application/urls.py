from django.urls import re_path, include,path
from application.views import * 
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    re_path(r'^mainpage$', pageproduct),
    re_path(r'^product$', product),
    path('google/', GoogleSocialAuthView.as_view()),
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginAPIView.as_view(), name="login"),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('email-verify/', VerifyEmail.as_view(), name="email-verify"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-reset-email/', RequestPasswordResetEmail.as_view(),
         name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/',
         PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete', SetNewPasswordAPIView.as_view(),
         name='password-reset-complete')
    # path('addhome',views.addHome),
]
from django.urls import path,include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView,TokenVerifyView,TokenBlacklistView
from .views import GoogleLoginView, GithubLoginView,Databases,LogoutView

router = routers.DefaultRouter()

urlpatterns = [
    path('auth/login', include(router.urls)),
    # path('databases/',Databases.as_view() , name='databases'),
    path('auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('auth/github/', GithubLoginView.as_view(), name='github_login'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/logout/', LogoutView.as_view(), name='token_blacklist'),

    # Otros endpoints de tu API
    # ...
]
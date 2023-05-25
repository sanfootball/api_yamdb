from rest_framework import routers
from django.urls import include, path

from .views import (
    ReviewViewSet,
    CommentViewSet,
    TitleViewSet,
    CategoryViewSet,
    GenreViewSet,
    UserViewSet,
    # UserUsernameViewSet,
    send_confirmation_code,
    send_token_jwt,
    data_request_from_users_me,
    # CategoryAPIView,
)

app_name = 'api'

router_v1 = routers.DefaultRouter()

router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('reviews', ReviewViewSet, basename='review')
router_v1.register('users', UserViewSet)
router_v1.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                   basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')

auth_v1 = [
    path('signup/', send_confirmation_code),
    path('token/', send_token_jwt),
]


urlpatterns = [
    path('v1/auth/', include(auth_v1)),
    path('v1/users/me/', data_request_from_users_me),
    path('v1/', include(router_v1.urls)),
]

from rest_framework import routers
from django.urls import include, path


from .views import (
    ReviewViewSet,
    CommentViewSet,
    UserViewSet,
    send_confirmation_code,
    send_token_jwt,
    CategoryAPIView,
    TitleAPIView, 
    GenreAPIView
)


app_name = 'api'

router_v1 = routers.DefaultRouter()

router_v1.register('reviews', ReviewViewSet, basename='review')
router_v1.register('titles', TitleAPIView, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)comments/',
    CommentViewSet, basename='comments')
router_v1.register('genres', GenreAPIView, basename='genres')
router_v1.register('categories', CategoryAPIView, basename='categories')
router_v1.register('users', UserViewSet)
router_v1.register('users/me', UserViewSet)

urlpatterns = [
    path('v1/auth/signup/', send_confirmation_code),
    path('v1/auth/token/', send_token_jwt),
    path('v1/', include(router_v1.urls)),
]

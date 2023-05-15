from rest_framework import routers
from django.urls import include, path

from .views import ReviewViewSet, CommentViewSet, CategoryAPIView

app_name = 'api'

router_v1 = routers.DefaultRouter()

router_v1.register('reviews', ReviewViewSet, basename='review')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews/', ReviewViewSet,
                   basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)comments/',
    CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/categories/', CategoryAPIView.as_view(),
         name='category-list-create-delete'),
]

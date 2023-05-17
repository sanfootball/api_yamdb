from rest_framework import routers
from django.urls import include, path


from .views import (
    ReviewViewSet,
    CommentViewSet,
    UserViewSet,
    UserUsernameViewSet,
    send_confirmation_code,
    send_token_jwt,
    data_request_from_users_me,
    # CategoryAPIView,
)


app_name = 'api'

router_v1 = routers.DefaultRouter()

router_v1.register('reviews', ReviewViewSet, basename='review')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews/', ReviewViewSet,
                   basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)comments/',
    CommentViewSet, basename='comments')

router_v1.register('users', UserViewSet)
router_v1.register('users/<str:username>', UserUsernameViewSet)

urlpatterns = [
    path('v1/auth/signup/', send_confirmation_code),
    path('v1/auth/token/', send_token_jwt),
    # path('v1/users/<str:username>', UserViewSet.as_view),
    path('v1/users/me/', data_request_from_users_me),
    path('v1/', include(router_v1.urls)),
    # path('v1/categories/', CategoryAPIView.as_view(),
    #      name='category-list-create-delete'),
]

# r'^[\w.@+-]+\Z'
# url(r'^profile/(?P<username>[\w.@+-]+)/$', views.user_profile),
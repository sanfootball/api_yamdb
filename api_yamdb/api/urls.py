from django.urls import path
from .views import CategoryAPIView

app_name = 'api'

urlpatterns = [
    path('v1/categories/', CategoryAPIView.as_view(),
         name='category-list-create-delete'),
]

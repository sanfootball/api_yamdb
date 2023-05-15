from rest_framework import filters, mixins, viewsets, pagination

from .permissions import IsAdminOrReadOnly


class CustomApiMixin(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):

    filter_backends = [filters.SearchFilter]
    pagination_class = [pagination.LimitOffsetPagination]
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    search_fields = ['=name']

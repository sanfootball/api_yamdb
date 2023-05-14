from rest_framework import generics, permissions
from reviews.models import Category
from .serializers import CategorySerializer


class CategoryAPIView(generics.ListCreateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        elif self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        elif self.request.method == 'DELETE':
            return [permissions.IsAdminUser()]

    # Метод get_queryset() переопределен для сортировки категорий по имени
    def get_queryset(self):
        return Category.objects.order_by('name')

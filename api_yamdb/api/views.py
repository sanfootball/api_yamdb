from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets, filters, mixins
from reviews.models import Category, Review, Title
from .serializers import CategorySerializer, ReviewSerializer, CommentSerializer

from reviews.models import Review, Title, User
from .serializers import (
    ReviewSerializer,
    CommentSerializer,
    SignupUserSerializer,
    TokenUserSerializer,
    UserUsernameSerializer,
    UserRetrieveSerializer,
    UserPartialUpdateSerializer,
    UserSerializer,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action, api_view, permission_classes

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAuthorOrModerOrAdmin, AdminPermissions, AccessUsersMe

from api.util import (
    confirmation_code_generation,
    send_confirmation_code_to_email,
)


class UserUsernameViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserUsernameSerializer
    lookup_field = 'username'
    permission_classes = (AdminPermissions, )
    http_method_names = ['get', 'patch', 'delete']
    
    # def get_serializer_class(self):
    #     """Выбор нужного сериализатора, в зависимости от значения action."""
    #     if self.action == 'retrieve':
    #         return UserRetrieveSerializer
    #     if self.action == 'partial_update':
    #         return UserPartialUpdateSerializer
    
    # def retrieve(self, request, username=None):
    #     queryset = User.objects.all()
    #     user = get_object_or_404(queryset, username=username)
    #     serializer = UserRetrieveSerializer(user)
    #     return Response(serializer.data)

    # def partial_update(self, request, username=None):
    #     queryset = User.objects.all()
    #     user = get_object_or_404(queryset, username=username)
    #     serializer = UserPartialUpdateSerializer(user)
    #     return Response(serializer.data) 


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAuthenticated, AdminPermissions)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', )

    # def create(self, request):
    #     if request.user.role == 'admin':
    #         serializer = UserSerializer(data=request.data)
    #         if serializer.is_valid(raise_exception=True):
    #             user = User.objects.create(
    #                 username=serializer.validated_data.get('username'),
    #                 email=serializer.validated_data.get('email'),
    #                 confirmation_code=confirmation_code_generation()
    #             )
    #             send_confirmation_code_to_email(user.confirmation_code, user.email)
    #             return Response(
    #                 serializer.data,
    #                 status=status.HTTP_201_CREATED,
    #             )
    #         return Response(
    #             serializer.error_messages,
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )
    #     return Response(
    #         # serializer.error_messages,
    #         status=status.HTTP_403_FORBIDDEN,
    #     )



# class CategoryAPIView(generics.ListCreateDestroyAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer

#     def get_permissions(self):
#         if self.request.method == 'GET':
#             return []
#         elif self.request.method == 'POST':
#             return [permissions.IsAdminUser()]
#         elif self.request.method == 'DELETE':
#             return [permissions.IsAdminUser()]

#     # Метод get_queryset() переопределен для сортировки категорий по имени
#     def get_queryset(self):
#         return Category.objects.order_by('name')


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModerOrAdmin, IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        new_queryset = title.reviews.all().order_by('id')
        return new_queryset

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModerOrAdmin, IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id')
        )
        new_queryset = review.comments.order_by('id')
        return new_queryset

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, review=review)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_confirmation_code(request):
    """
    Обработка данных пользователя поступивших с api/v1/auth/signup/
    и отправка confirmation_code на email пользователя.
    """
    if User.objects.filter(username=request.data.get('username')).exists():
        if User.objects.get(
            username=request.data.get('username')
        ).email != request.data.get('email'):
            return Response(
                request.data,
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.get(username=request.data.get('username'))
        user.confirmation_code = confirmation_code_generation()
        user.save(update_fields=['confirmation_code'])
        send_confirmation_code_to_email(user.confirmation_code, user.email)

        return Response(
            request.data,
            status=status.HTTP_200_OK,
        )
    serializer = SignupUserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        confirmation_code = confirmation_code_generation()
        user = User.objects.create(
            username=serializer.validated_data.get('username'),
            email=serializer.validated_data.get('email'),
            confirmation_code=confirmation_code
        )
        send_confirmation_code_to_email(user.confirmation_code, user.email)
        
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    return Response(
        serializer.error_messages,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_token_jwt(request):
    """
    Обработка данных поступивших с api/v1/auth/token/
    и возвращение в ответ на запрос access токен.
    """
    serializer = TokenUserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if user.confirmation_code == confirmation_code:
            access_jwt_token = AccessToken.for_user(user)
            return Response(
                f'token: {access_jwt_token}',
                status=status.HTTP_200_OK,
            )
        return Response(
            'Введен не верный confirmation_code.',
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response(
        serializer.error_messages,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated, ])
def data_request_from_users_me(request):
    """предоставление данных учетной записи пользователя."""
    user = request.user
    if request.method == 'GET':
        serializer = UserRetrieveSerializer(user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
    if request.method == 'PATCH' and 'role' not in request.data:
        serializer = UserPartialUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

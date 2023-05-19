from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework import viewsets, filters, permissions
from reviews.models import Category, Review, Title, User, Genre
from django_filters.rest_framework import DjangoFilterBackend
from .mixins import ListCreateDestroyViewSet
from .serializers import (
    CategorySerializer,
    ReviewSerializer,
    CommentSerializer,
    GenreSerializer,
    TitlesEditorSerializer,
    TitlesReadSerializer,
    SignupUserSerializer,
    TokenUserSerializer,
    UserUsernameSerializer,
    UserRetrieveSerializer,
    UserPartialUpdateSerializer,
    CreateUserSerializer,
    UserSerializer,
)
from rest_framework import status
from .filters import TitleFilter
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    AllowAny,
    IsAuthenticated,
)
from rest_framework.pagination import PageNumberPagination
from .permissions import (
    IsAuthorOrModerOrAdmin,
    AdminPermissions,
    IsAdminOrReadOnly,
    AccessUsersMe,
)

from rest_framework.decorators import action, api_view, permission_classes

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.util import (
    confirmation_code_generation,
    send_confirmation_code_to_email,
    http_methods_disable,
)


# class UserUsernameViewSet(viewsets.ModelViewSet):
#    queryset = User.objects.all()
#    serializer_class = UserUsernameSerializer
#    lookup_field = 'username'
#    permission_classes = (AdminPermissions, )
#    http_method_names = ['get', 'patch', 'delete']

#    def get_serializer_class(self):
#        """Выбор нужного сериализатора, в зависимости от значения action."""
#        if self.action == 'retrieve':
#            return UserRetrieveSerializer
#        if self.action == 'partial_update':
#            return UserPartialUpdateSerializer

#    def retrieve(self, request, username=None):
#        queryset = User.objects.all()
#        user = get_object_or_404(queryset, username=username)
#        serializer = UserRetrieveSerializer(user)
#        return Response(serializer.data)

#    def partial_update(self, request, username=None):
#        queryset = User.objects.all()
#        user = get_object_or_404(queryset, username=username)
#        serializer = UserPartialUpdateSerializer(user)
#        return Response(serializer.data)


@http_methods_disable('put')
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserUsernameSerializer
    lookup_field = 'username'
    permission_classes = (IsAuthenticated, AdminPermissions)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', )

    def get_serializer_class(self):
        if self.request.method == 'POST':  # and (self.request.user.is_staff or self.request.user.is_superuser):
            return CreateUserSerializer
        return UserUsernameSerializer

    # def create(self, request):
    #     if request.user.role == 'admin':
    #         serializer = UserSerializer(data=request.data)
    #         if serializer.is_valid(raise_exception=True):
    #             user = User.objects.create(
    #                 username=serializer.validated_data.get('username'),
    #                 email=serializer.validated_data.get('email'),
    #                 confirmation_code=confirmation_code_generation()
    #             )
    #             send_confirmation_code_to_email(
    #                 user.confirmation_code, user.email)
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
    user = get_object_or_404(User, username=request.user.username)
    if request.method == 'GET':
        serializer = UserRetrieveSerializer(user, data=request.data,
                                            partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    if request.method == 'PATCH' and 'role' not in request.data:
        serializer = UserPartialUpdateSerializer(
            user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


# class CategoryAPIView(generics.ListCreateAPIView):
#   queryset = Category.objects.all()
#   serializer_class = CategorySerializer
#
#   def get_permissions(self):
#       if self.request.method == 'GET':
#           return []
#       elif self.request.method == 'POST':
#           return [permissions.IsAdminUser()]
#       elif self.request.method == 'DELETE':
#           return [permissions.IsAdminUser()]
#
#   # Метод get_queryset() переопределен для сортировки категорий по имени
#   def get_queryset(self):
#       return Category.objects.order_by('name')


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminPermissions,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitlesEditorSerializer
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    # def get_queryset(self):
    #    new_queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    #    return new_queryset

    def get_serializer_class(self):
        if (
            self.request.user.is_authenticated is False
            or self.request.method in permissions.SAFE_METHODS
        ):
            return TitlesReadSerializer
        return TitlesEditorSerializer


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminPermissions,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModerOrAdmin, IsAuthenticated)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        new_queryset = title.reviews.all().order_by('id')
        return new_queryset

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModerOrAdmin, IsAuthenticated)

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

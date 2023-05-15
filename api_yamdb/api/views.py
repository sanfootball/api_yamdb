from rest_framework import filters, viewsets
from django.shortcuts import get_object_or_404

from reviews.models import Review, Title, User
from .serializers import (
    ReviewSerializer,
    CommentSerializer,
    SignupUserSerializer,
    TokenUserSerializer,
    UserSerializer,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action, api_view, permission_classes

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAuthorOrModerOrAdmin, AdminPermissions

from api.util import (
    confirmation_code_generation,
    send_confirmation_code_to_email,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAuthenticated, AdminPermissions)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', )

    # @action(
    #     methods=['get', 'patch'],
    #     detail=True,
    #     url_path='me',
    #     serializer_class=UserSerializer,
    #     permission_classes=[IsAuthorOrModerOrAdmin, ],
    # )
    # def users_me(self, request, pk=None):
    #     user = request.user
    #     if request.method == 'GET':
    #         serializer = self.get_serializer(user, data=request.data, partial=True)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response(
    #             serializer.data,
    #             status=status.HTTP_200_OK,
    #         )
    #     if request.method == 'PATCH':
    #         serializer = self.get_serializer(user)
    #         return Response(
    #             serializer.data,
    #             status=status.HTTP_200_OK,
    #         )


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

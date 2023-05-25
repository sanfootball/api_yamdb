from rest_framework import serializers
from django.shortcuts import get_object_or_404

from api_yamdb.settings import PATTERN, PATTERN_SLUG
from reviews.models import Review, Comment, Category, User, Genre, Title

from django.forms import ValidationError
from rest_framework.validators import UniqueValidator
from django.contrib.auth.validators import UnicodeUsernameValidator


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class ReviewSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(max_value=10, min_value=1)
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date', 'score')
        model = Review

    def validate(self, data):
        request = self.context['request']
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title,
                                      author=request.user).exists()
        ):
            raise ValidationError(
                'Более 1 отзыва на произведение не доступно')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('author', 'pub_date')


class GenreSerializer(serializers.ModelSerializer):
    slug = serializers.RegexField(
        regex=PATTERN_SLUG,
        max_length=50,
        validators=[
            UniqueValidator(queryset=Genre.objects.all()),
        ],
    )

    class Meta:
        model = Genre
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
        fields = ('name', 'slug')


class TitlesReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitlesEditorSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'


class SignupUserSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(regex=PATTERN, max_length=150)
    email = serializers.EmailField(
        max_length=254,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            UnicodeUsernameValidator(),
        ]
    )

    class Meta:
        model = User
        fields = ['email', 'username']

    def validate_username(self, value):
        """Валидация поля username, которое не должно использовать имя me."""
        if 'me' == value:
            raise serializers.ValidationError(
                'Имя me недоступно для пользователей',
            )
        return value


class TokenUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
    )

    class Meta:
        model = User
        fields = ['confirmation_code', 'username']


class UserSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(regex=PATTERN, max_length=150)
    email = serializers.EmailField(
        max_length=254,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            UnicodeUsernameValidator(),
        ]
    )
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def validate_username(self, value):
        """Валидация поля username, которое не должно использовать имя me."""
        if 'me' == value:
            raise serializers.ValidationError(
                'Имя me недоступно для пользователей',
            )
        return value


class UserUsernameSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class CreateUserSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        regex=PATTERN,
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            UnicodeUsernameValidator(),
        ]
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def validate_username(self, value):
        """Валидация поля username, которое не должно использовать имя me."""
        if 'me' == value:
            raise serializers.ValidationError(
                'Имя me недоступно для пользователей',
            )
        return value

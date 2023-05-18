from rest_framework import serializers
from api_yamdb.settings import PATTERN
from reviews.models import Review, Comment, Category, User

from django.forms import ValidationError
from rest_framework.validators import UniqueValidator
from django.contrib.auth.validators import UnicodeUsernameValidator


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')


class CategoryActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')

    def create(self, validated_data):
        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

    def delete(self, instance):
        instance.delete()


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['title_id']
        if request.method == 'POST':
            if Review.objects.filter(title=title_id,
                                     author=request.user).exists():
                raise ValidationError(
                    'Более 1 отзыва на произведение не допустимо')
        return data

    def validate_score(self, score):
        if score < 1 or score > 10:
            raise serializers.ValidationError(
                'Рейтинг произведения должен быть от 1 до 10')
        return score

    class Meta:
        fields = ('id', 'title', 'text', 'author', 'pub_date', 'score')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    review = serializers.ReadOnlyField(source='review.id')

    class Meta:
        model = Comment
        fields = ('id', 'review', 'text', 'author', 'pub_date')
        read_only_fields = ('author', 'review', 'pub_date')


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
    # role = serializers.ChoiceField(max_length=150)

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
    # role = serializers.ChoiceField(max_length=150)

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


class UserRetrieveSerializer(serializers.ModelSerializer):
    """Обрабатывает запрос на предоставление данных учетной записи."""
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


class UserPartialUpdateSerializer(serializers.ModelSerializer):
    """Обрабатывает запрос частичное изменение данных учетной записи."""
    username = serializers.RegexField(regex=PATTERN, max_length=150)
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

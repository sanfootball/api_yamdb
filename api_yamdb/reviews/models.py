import datetime
from django.db import models
from api_yamdb.settings import SHOW_WORDS
from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator, MinValueValidator)


class User(AbstractUser):
    """Кастомная модель пользователей."""
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (USER, 'аутентифицированный пользователь'),
        (MODERATOR, 'модератор'),
        (ADMIN, 'администратор'),
    )
    username = models.CharField(
        'никнейм пользователя',
        max_length=150,
        null=True,
        unique=True,
    )
    email = models.EmailField(
        max_length=254,
        null=True,
        unique=True,
    )
    first_name = models.CharField('Имя пользователя',
                                  max_length=150,
                                  null=True,)
    last_name = models.CharField('Фамилия пользователя',
                                 max_length=150,
                                 null=True,)
    bio = models.TextField('О пользователе', null=True,)
    role = models.CharField(choices=ROLE_CHOICES, default=USER, max_length=150)
    confirmation_code = models.CharField(max_length=150)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def str(self) -> str:
        if self.username is not None:
            return self.username
        return 'NULL'


class Category(models.Model):
    """Модель категорий произведений."""
    name = models.CharField('Название категории', max_length=256)
    slug = models.SlugField('slug категории', unique=True, max_length=50)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    """Модель жанров произведений."""
    name = models.CharField('Название жанра', max_length=256)
    slug = models.CharField('slug жанра', unique=True, max_length=50)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self) -> str:
        return self.name


class Title(models.Model):
    """Модель произведений."""
    name = models.CharField('Название произведения', max_length=256)
    year = models.SmallIntegerField(
        verbose_name='Год выпуска',
        validators=[
            MaxValueValidator(
                datetime.datetime.now().year,
                message='Год выпуска не должен быть в будущем времени')])
    description = models.TextField('Описание')
    genre = models.ManyToManyField(
        Genre,
        related_name='titles'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
    )

    class Meta:
        verbose_name = 'Название'
        verbose_name_plural = 'Названия'

    def __str__(self) -> str:
        return self.name


class TitleGenre(models.Model):
    """Промежуточная модель для реализации отношения многие ко многим."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='titles'
    )

    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр',
        related_name='genres',
    )

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'genre'],
                name='unique_title_genre_pair'
            )
        ]

    def __str__(self) -> str:
        return f'{self.title}, жанр - {self.genre}'


class Review(models.Model):
    """Модель отзывов к произведениям."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )

    score = models.PositiveSmallIntegerField(
        default=0,
        null=True,
        blank=True,
        validators=(MinValueValidator(1, 'Оценка должна быть от 1 до 10'),
                    MaxValueValidator(10, 'Оценка должна быть от 1 до 10'))
    )
    pub_date = models.DateTimeField(
        'Дата и время публикации отзыва',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_title_author'
            )
        ]

    def str(self) -> str:
        return self.text[:SHOW_WORDS]


class Comment(models.Model):
    """Модель комментариев к отзывам."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    pub_date = models.DateTimeField(
        'Дата и время публикации комментария',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.text

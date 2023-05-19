from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
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
        validators=[
            RegexValidator(regex=r'^[\w.@+-]+\Z')
        ]
    )
    email = models.EmailField(
        max_length=254,
        null=True,
        unique=True,
    )
    first_name = models.CharField('имя пользователя', max_length=150, null=True,)
    last_name = models.CharField('фамилия пользователя', max_length=150, null=True,)
    bio = models.TextField('о пользователе', null=True,)
    role = models.CharField(choices=ROLE_CHOICES, default=USER, max_length=150)
    confirmation_code = models.CharField(max_length=150)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self) -> str:
        return self.username


class Category(models.Model):
    name = models.CharField('название категории', max_length=256)
    slug = models.SlugField('slug категории', unique=True, max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    name = models.CharField('название жанра', max_length=256)
    slug = models.CharField('slug жанра', unique=True, max_length=50)

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'жанры'

    def __str__(self) -> str:
        return self.name


class Title(models.Model):
    name = models.CharField('название произведения', max_length=256)
    year = models.IntegerField('год выпуска')
    description = models.TextField('описание')
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
    )

    class Meta:
        verbose_name = 'название'
        verbose_name_plural = 'названия'

    def __str__(self) -> str:
        return self.name

    
class TitleGenre(models.Model):
    
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name = 'произведение'
    )

    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name = 'жанр'
    )

    class Meta:
        verbose_name = 'произведение и жанр'
        verbose_name_plural = 'произведения и жанры'

    def __str__(self) -> str:
        return f'{self.title}, жанр - {self.genre}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.TextField('текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )

    score = models.IntegerField(default=0, null=True, blank=True)
    pub_date = models.DateTimeField(
        'дата и время публикации отзыва',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField('текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    pub_date = models.DateTimeField(
        'дата и время публикации комментария',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.text

from django.contrib import admin

from .models import User, Category, Genre, Title, Review, Comment


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


@admin.register(User)
class UserAdmin(BaseAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'role',
    )
    search_fields = ('username',)
    list_filter = ('username',)


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Genre)
class GenreAdmin(BaseAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Title)
class TitleAdmin(BaseAdmin):
    list_display = (
        'name',
        'year',
        'description',
        'category',
    )

    search_fields = ('name',)
    list_filter = ('name', 'year')


@admin.register(Review)
class ReviewAdmin(BaseAdmin):
    list_display = (
        'title',
        'text',
        'author',
        'score',
        'pub_date',
    )

    search_fields = ('title',)
    list_filter = ('title', 'pub_date')


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
    list_display = (
        'review',
        'text',
        'author',
        'pub_date',
    )
    search_fields = ('author',)
    list_filter = ('author',)

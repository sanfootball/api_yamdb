from django.contrib import admin
from .models import User


admin.site.register(User)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


# @admin.register(User)
# class UserAdmin(BaseAdmin):
#     list_display = (
#         'username',
#         'email',
#         'first_name',
#         'last_name',
#         'bio',
#         'role',
#     )
#     search_fields = ('username',)
#     list_filter = ('username',)

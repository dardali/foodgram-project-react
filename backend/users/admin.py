from django.contrib import admin

from .models import CustomUser, Subscribe


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('username',)
    list_filter = ('email', 'first_name',)
    empty_value_display = '-пусто-'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )

from django.contrib import admin
from .models import Group, Post


class GroupAdmin(admin.ModelAdmin):
    actions = None
    list_display = (
        'title',
        'slug',
        'description',
    )
    list_editable = ('title',)
    search_fields = ('slug',)
    list_filter = ('description',)
    empty_value_display = '-пусто-'
    list_display_links = None


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)

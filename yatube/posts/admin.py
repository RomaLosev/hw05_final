from django.contrib import admin
from .models import Group, Post, Comment, Follow


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
    
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'text',
        'created',
        'author',
    )
    list_editable = ('text',)
    search_fields = ('post',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'
    list_display_links = None

class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    list_editable = ('author',)
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'
    list_display_links = None 


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)

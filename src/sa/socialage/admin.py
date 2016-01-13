from django.contrib import admin

from .models import *

# Register your models here.


class PageInline(admin.TabularInline):
    model = Page
    list_display = ('name', 'id')


class LikeInline(admin.TabularInline):
    model = FacebookPageLike


class FollowInLine(admin.TabularInline):
    model = TwitterFollow


class UserAdmin(admin.ModelAdmin):
    inlines = [LikeInline, FollowInLine]
    list_display = ('name', 'id', 'birthday', 'age')


class PageAdmin(admin.ModelAdmin):
    list_display = ('name', 'tw_handle', 'fb_handle', 'total', 'avg_age')


class AgeTableAdmin(admin.ModelAdmin):
    list_display = ('id','table')

admin.site.register(Page, PageAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(AgeTable, AgeTableAdmin)

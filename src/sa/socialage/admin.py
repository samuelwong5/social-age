from django.contrib import admin

from .models import *


# Register your models here.
class PageInline(admin.TabularInline):
    model = FacebookPage
    list_display = ('name', 'id')


class LikeInline(admin.TabularInline):
    model = FacebookPageLike


class UserAdmin(admin.ModelAdmin):
    inlines = [LikeInline]
    list_display = ('name', 'id', 'birthday')


class PageAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')


admin.site.register(FacebookPage, PageAdmin)
admin.site.register(FacebookUser, UserAdmin)

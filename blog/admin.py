from django.contrib import admin
from .models import Blog, Category

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

from django.contrib import admin
from .models import Blog, Category, Tag, BlogReactions, BlogSubmission, BlogView

# @admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'created_at')
    list_filter = ('is_published', 'category')
    search_fields = ('title', 'content')
    filter_horizontal = ('tags',)  # Apply only to ManyToManyField


admin.site.register(Category, CategoryAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Tag)
admin.site.register(BlogReactions)
admin.site.register(BlogSubmission)

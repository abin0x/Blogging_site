from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Blog(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    featured_image = models.URLField(null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='blogs')  # Single category
    tags = models.ManyToManyField(Tag, related_name='blogs')  # Change to ManyToManyField

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    good_reactions = models.PositiveIntegerField(default=0)  # Count of "Good" reactions
    bad_reactions = models.PositiveIntegerField(default=0)  # Count of "Bad" reactions
    views_count = models.PositiveIntegerField(default=0)  # Count of views

    def __str__(self):
        return self.title


class BlogReaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="reactions")
    reaction = models.CharField(max_length=10, choices=[('good', 'Good'), ('bad', 'Bad')])

    class Meta:
        unique_together = ('user', 'blog')

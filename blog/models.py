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
    # author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    author = models.CharField(max_length=255)
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



class BlogReactions(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # reaction = models.CharField(max_length=10, choices=[('good', 'Good'), ('bad', 'Bad')])
    reaction = models.CharField(max_length=10, choices=[('good', 'Good'), ('bad', 'Bad')], default='good')  

    class Meta:
        unique_together = ('blog', 'user')

class BlogView(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blog', 'user', 'session_key')  # Ensure unique views by user or session

    def __str__(self):
        if self.user:
            return f"View of {self.blog.title} by {self.user.username}"
        return f"Anonymous view of {self.blog.title} (session {self.session_key})"




class BlogSubmission(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    user = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    


# models.py
from django.db import models

class MediaItem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    youtube_url = models.URLField()
    thumbnail = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    media_type = models.CharField(max_length=10, choices=[('audio', 'Audio'), ('video', 'Video')])

    def __str__(self):
        return self.title
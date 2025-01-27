from rest_framework import serializers
from .models import Blog, Category, Tag, BlogReactions, BlogView
from django.utils.translation import activate
from django.utils import timezone

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']



class BlogSerializer(serializers.ModelSerializer):
    author = serializers.CharField()  
    # author = serializers.StringRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Accept category ID
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)  # Accept tag IDs
    good_reactions_count = serializers.IntegerField(read_only=True)
    bad_reactions_count = serializers.IntegerField(read_only=True)
    views_count = serializers.IntegerField(read_only=True)
    reading_time = serializers.IntegerField(read_only=True)  # Add reading time field

    def to_representation(self, instance):
        # Activate Bengali locale for the datetime fields
        activate('bn')
        
        # Customize representation to show names for category and tags
        representation = super().to_representation(instance)

        # Format created_at and updated_at in Bengali date-time format
        representation['created_at'] = instance.created_at.astimezone(timezone.get_current_timezone()).strftime('%d %B, %Y - %I:%M%p')
        representation['updated_at'] = instance.updated_at.astimezone(timezone.get_current_timezone()).strftime('%d %B, %Y - %I:%M%p')
        representation['category'] = {
            'id': instance.category.id,
            'name': instance.category.name
        }
        representation['tags'] = [
            {'id': tag.id, 'name': tag.name} for tag in instance.tags.all()
        ]

        # Add counts for reactions
        good_reactions = BlogReactions.objects.filter(blog=instance, reaction='good').count()
        bad_reactions = BlogReactions.objects.filter(blog=instance, reaction='bad').count()

        representation['good_reactions_count'] = good_reactions
        representation['bad_reactions_count'] = bad_reactions

        # Add views count
        views = BlogView.objects.filter(blog=instance).count()
        representation['views_count'] = views

        # Estimate reading time based on content length (average reading speed 250 words per minute)
        word_count = len(instance.content.split())  # Count the words in the content
        reading_time_minutes = word_count // 200  # Estimate reading time in minutes
        if word_count % 200 > 0:
            reading_time_minutes += 1  # Round up if not a complete minute
        representation['reading_time'] = reading_time_minutes


        return representation

    class Meta:
        model = Blog
        fields = [
            'id', 'author', 'title', 'content',
            'category', 'tags', 'featured_image',
            'is_published', 'created_at', 'updated_at',
            'good_reactions_count', 'bad_reactions_count', 'views_count','reading_time'
        ]

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        blog = Blog.objects.create(**validated_data)
        blog.tags.set(tags)  # Associate tags with the blog
        return blog

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.tags.set(tags)  # Update tags
        instance.save()
        return instance




class BlogReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogReactions
        fields = ['id', 'blog', 'user', 'reaction']
        read_only_fields = ['user']




# from rest_framework import serializers
# from .models import BlogSubmission
# from django.core.mail import send_mail

# class BlogSubmissionSerializer(serializers.ModelSerializer):
#     user = serializers.StringRelatedField(read_only=True)  # Display username

#     class Meta:
#         model = BlogSubmission
#         fields = ['id', 'title', 'content', 'name', 'phone_number', 'user', 'created_at']

#     def create(self, validated_data):
#         user = self.context['request'].user
#         validated_data['user'] = user
#         blog_submission = BlogSubmission.objects.create(**validated_data)

#         # Send email
#         send_mail(
#             subject=blog_submission.title,
#             message=f"Blog Title: {blog_submission.title}\n"
#                     f"Author Name: {blog_submission.name}\n"
#                     f"Phone: {blog_submission.phone_number}\n\n"
#                     f"Content:\n{blog_submission.content}",
#             from_email="mahmudulabin@gmail.com",
#             recipient_list=["4819abin@gmail.com"],
#             fail_silently=False,
#         )
#         return blog_submission

from rest_framework import serializers
from .models import BlogSubmission
from django.core.mail import send_mail
from django.template.loader import render_to_string

class BlogSubmissionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Display username

    class Meta:
        model = BlogSubmission
        fields = ['id', 'title', 'content', 'name', 'phone_number', 'user', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        blog_submission = BlogSubmission.objects.create(**validated_data)

        # Render HTML email content
        email_subject = blog_submission.title
        email_body = render_to_string('email/blog_submission_email.html', {
            'title': blog_submission.title,
            'name': blog_submission.name,
            'phone_number': blog_submission.phone_number,
            'content': blog_submission.content,
            'user': blog_submission.user,
        })

        # Send the email with HTML body
        send_mail(
            subject=email_subject,
            message="",  # Leave the plain text message empty as we're using HTML
            from_email="mahmudulabin@gmail.com",
            recipient_list=["4819abin@gmail.com"],
            html_message=email_body,  # This is where we pass the HTML email body
            fail_silently=False,
        )
        return blog_submission

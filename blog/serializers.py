from rest_framework import serializers
from .models import Blog, Category, Tag, BlogReactions, BlogView

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

# class BlogSerializer(serializers.ModelSerializer):
#     author = serializers.StringRelatedField(read_only=True)
#     category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Accept category ID
#     tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)  # Accept tag IDs

#     def to_representation(self, instance):
#         # Customize representation to show names for category and tags
#         representation = super().to_representation(instance)
#         representation['category'] = {
#             'id': instance.category.id,
#             'name': instance.category.name
#         }
#         representation['tags'] = [
#             {'id': tag.id, 'name': tag.name} for tag in instance.tags.all()
#         ]
#         return representation

#     class Meta:
#         model = Blog
#         fields = [
#             'id', 'author', 'title', 'content',
#             'category', 'tags', 'featured_image',
#             'is_published', 'created_at', 'updated_at'
#         ]


#     def create(self, validated_data):
#         tags = validated_data.pop('tags', [])
#         blog = Blog.objects.create(**validated_data)
#         blog.tags.set(tags)  # Associate tags with the blog
#         return blog

#     def update(self, instance, validated_data):
#         tags = validated_data.pop('tags', [])
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.tags.set(tags)  # Update tags
#         instance.save()
#         return instance


class BlogSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Accept category ID
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)  # Accept tag IDs
    good_reactions_count = serializers.IntegerField(read_only=True)
    bad_reactions_count = serializers.IntegerField(read_only=True)
    views_count = serializers.IntegerField(read_only=True)

    def to_representation(self, instance):
        # Customize representation to show names for category and tags
        representation = super().to_representation(instance)
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

        return representation

    class Meta:
        model = Blog
        fields = [
            'id', 'author', 'title', 'content',
            'category', 'tags', 'featured_image',
            'is_published', 'created_at', 'updated_at',
            'good_reactions_count', 'bad_reactions_count', 'views_count'
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
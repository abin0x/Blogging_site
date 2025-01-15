from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Blog, Category, Tag
from .serializers import BlogSerializer, CategorySerializer, TagSerializer, BlogReactionSerializer
from rest_framework.filters import SearchFilter
from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status


# Blog Views
class BlogListCreateAPIView(generics.ListCreateAPIView):
    queryset = Blog.objects.filter(is_published=True)
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Authenticated users can create

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)



class BlogDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Authenticated users can modify

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.author:
            raise PermissionDenied("You do not have permission to delete this blog.")
        instance.delete()


# Category Views
class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Allow anyone to view, but restrict creation to authenticated users

    def perform_create(self, serializer):
        serializer.save()

# Tag Views
class TagListCreateAPIView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Allow anyone to view, but restrict creation to authenticated users

    def perform_create(self, serializer):
        serializer.save()


# Blog Search View
class BlogSearchAPIView(ListAPIView):
    serializer_class = BlogSerializer

    def get_queryset(self):
        queryset = Blog.objects.filter(is_published=True)  # Only show published blogs
        search_query = self.request.query_params.get('q', None)  # Get the search query

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |  # Search by title
                Q(content__icontains=search_query) |  # Search by content
                Q(tags__icontains=search_query)  # Search by tags
            ).distinct()  # Ensure distinct results in case of multiple matches
        return queryset

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .serializers import BlogReactionSerializer

# class BlogReactionAPIView(APIView):
#     def get(self, request, pk):
#         """
#         Retrieve a blog and increment its views count.
#         """
#         try:
#             blog = Blog.objects.get(pk=pk, is_published=True)
#             blog.views_count += 1  # Increment the view count
#             blog.save(update_fields=['views_count'])
#             serializer = BlogReactionSerializer(blog)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Blog.DoesNotExist:
#             return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)

#     def post(self, request, pk):
#         """
#         Allow users to react to a blog (Good or Bad).
#         """
#         try:
#             blog = Blog.objects.get(pk=pk, is_published=True)
#             reaction = request.data.get('reaction')  # 'good' or 'bad'

#             if reaction == 'good':
#                 blog.good_reactions += 1
#             elif reaction == 'bad':
#                 blog.bad_reactions += 1
#             else:
#                 return Response({'error': 'Invalid reaction'}, status=status.HTTP_400_BAD_REQUEST)

#             blog.save(update_fields=['good_reactions', 'bad_reactions'])
#             serializer = BlogReactionSerializer(blog)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Blog.DoesNotExist:
#             return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)




# class BlogReactionAPIView(generics.RetrieveUpdateAPIView):
#     queryset = Blog.objects.filter(is_published=True)
#     serializer_class = BlogReactionSerializer

#     def retrieve(self, request, *args, **kwargs):
#         """
#         Retrieve a blog and increment its views count.
#         """
#         blog = self.get_object()
#         blog.views_count += 1  # Increment the view count
#         blog.save(update_fields=['views_count'])
#         serializer = self.get_serializer(blog)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def update(self, request, *args, **kwargs):
#         """
#         Allow users to react to a blog (Good or Bad), ensuring only one reaction per user.
#         """
#         blog = self.get_object()
#         user = request.user
#         reaction = request.data.get('reaction')  # 'good' or 'bad'

#         if reaction not in ['good', 'bad']:
#             raise ValidationError({'error': 'Invalid reaction'})

#         # Check if the user has already reacted
#         user_reaction, created = BlogReaction.objects.get_or_create(user=user, blog=blog)

#         if not created and user_reaction.reaction == reaction:
#             return Response({'error': 'You have already reacted with this choice'}, status=status.HTTP_400_BAD_REQUEST)

#         # Update or set the user's reaction
#         if user_reaction.reaction == 'good':
#             blog.good_reactions -= 1
#         elif user_reaction.reaction == 'bad':
#             blog.bad_reactions -= 1

#         user_reaction.reaction = reaction
#         user_reaction.save()

#         if reaction == 'good':
#             blog.good_reactions += 1
#         elif reaction == 'bad':
#             blog.bad_reactions += 1

#         blog.save(update_fields=['good_reactions', 'bad_reactions'])
#         serializer = self.get_serializer(blog)
#         return Response(serializer.data, status=status.HTTP_200_OK)




class BlogReactionAPIView(generics.RetrieveUpdateAPIView):
    queryset = Blog.objects.filter(is_published=True)
    serializer_class = BlogReactionSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a blog and increment its views count.
        """
        blog = self.get_object()
        blog.views_count += 1  # Increment the view count
        blog.save(update_fields=['views_count'])
        
        # Return the Blog data, including reaction counts
        blog_serializer = BlogSerializer(blog)
        return Response(blog_serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        Allow users to react to a blog (Good or Bad), ensuring only one reaction per user.
        """
        blog = self.get_object()
        user = request.user
        reaction = request.data.get('reaction')  # 'good' or 'bad'

        if reaction not in ['good', 'bad']:
            raise ValidationError({'error': 'Invalid reaction'})

        # Check if the user has already reacted
        user_reaction, created = BlogReaction.objects.get_or_create(user=user, blog=blog)

        if not created and user_reaction.reaction == reaction:
            return Response({'error': 'You have already reacted with this choice'}, status=status.HTTP_400_BAD_REQUEST)

        # Update or set the user's reaction
        if user_reaction.reaction == 'good':
            blog.good_reactions -= 1
        elif user_reaction.reaction == 'bad':
            blog.bad_reactions -= 1

        user_reaction.reaction = reaction
        user_reaction.save()

        if reaction == 'good':
            blog.good_reactions += 1
        elif reaction == 'bad':
            blog.bad_reactions += 1

        blog.save(update_fields=['good_reactions', 'bad_reactions'])
        
        # Return the Blog data, including updated reaction counts
        blog_serializer = BlogSerializer(blog)
        return Response(blog_serializer.data, status=status.HTTP_200_OK)

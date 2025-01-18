from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Blog, Category, Tag, BlogReactions, BlogView
from .serializers import BlogSerializer, CategorySerializer, TagSerializer, BlogReactionSerializer
from rest_framework.filters import SearchFilter
from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
import hashlib


class BlogReactionAPIView(generics.CreateAPIView):
    serializer_class = BlogReactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Blog Views
class BlogListCreateAPIView(generics.ListCreateAPIView):
    queryset = Blog.objects.filter(is_published=True)
    serializer_class = BlogSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]  

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)



class BlogDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.author:
            raise PermissionDenied("You do not have permission to delete this blog.")
        instance.delete()
    
    def get(self, request, *args, **kwargs):
        blog = self.get_object()

        # Track views for both authenticated and non-authenticated users
        if request.user.is_authenticated:
            # Logged-in users: track by user ID
            if not BlogView.objects.filter(blog=blog, user=request.user).exists():
                BlogView.objects.create(blog=blog, user=request.user)
        else:
            # Non-authenticated users: track by session or IP
            client_ip = self.get_client_ip(request)
            session_key = hashlib.md5(client_ip.encode() + str(blog.id).encode()).hexdigest()

            if not BlogView.objects.filter(blog=blog, session_key=session_key).exists():
                BlogView.objects.create(blog=blog, session_key=session_key)

        return self.retrieve(request, *args, **kwargs)

    def get_client_ip(self, request):
        """Helper function to get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


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


# class BlogReactionAPIView(generics.UpdateAPIView):
#     queryset = Blog.objects.all()
#     serializer_class = BlogReactionSerializer
#     permission_classes = [IsAuthenticated]

#     def update(self, request, *args, **kwargs):
#         blog = self.get_object()
#         user = request.user
#         reaction = request.data.get('reaction')

#         if reaction not in ['good', 'bad']:
#             raise ValidationError({'error': 'Invalid reaction type.'})

#         user_reaction, created = BlogReactions.objects.get_or_create(user=user, blog=blog)

#         if not created and user_reaction.reaction == reaction:
#             return Response({'error': 'You have already reacted with this choice.'}, status=status.HTTP_400_BAD_REQUEST)

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
#         return Response({'message': 'Reaction updated successfully.'}, status=status.HTTP_200_OK)

class BlogReactionAPIView(generics.UpdateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogReactionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Allow any user (authenticated or non-authenticated)

    def update(self, request, *args, **kwargs):
        blog = self.get_object()  # Get the Blog object from the URL parameters
        reaction = request.data.get('reaction')  # Get the reaction from the request body

        # Validate that the reaction is either 'good' or 'bad'
        if reaction not in ['good', 'bad']:
            raise ValidationError({'error': 'Invalid reaction type. Use either "good" or "bad".'})

        # Handle authenticated users
        if request.user.is_authenticated:
            user = request.user  # Get the authenticated user
            user_reaction, created = BlogReactions.objects.get_or_create(user=user, blog=blog)
        else:
            # Handle non-authenticated users by using session or IP
            client_ip = self.get_client_ip(request)
            session_key = hashlib.md5(client_ip.encode() + str(blog.id).encode()).hexdigest()

            # For non-authenticated users, use session_key as the unique identifier
            user_reaction, created = BlogReactions.objects.get_or_create(session_key=session_key, blog=blog)

        # If the reaction is the same as before, return an error
        if not created and user_reaction.reaction == reaction:
            return Response({'error': 'You have already reacted with this choice.'}, status=status.HTTP_400_BAD_REQUEST)

        # Decrement the old reaction count
        if user_reaction.reaction == 'good':
            blog.good_reactions -= 1
        elif user_reaction.reaction == 'bad':
            blog.bad_reactions -= 1

        # Update the reaction to the new one (either 'good' or 'bad')
        user_reaction.reaction = reaction
        user_reaction.save()  # Save the updated reaction

        # Increment the respective reaction count
        if reaction == 'good':
            blog.good_reactions += 1
        elif reaction == 'bad':
            blog.bad_reactions += 1

        # Save the updated blog object with new reaction counts
        blog.save(update_fields=['good_reactions', 'bad_reactions'])

        # Return a success message
        return Response({'message': 'Reaction updated successfully.'}, status=status.HTTP_200_OK)

    def get_client_ip(self, request):
        """Helper function to get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
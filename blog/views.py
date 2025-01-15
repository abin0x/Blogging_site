from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Blog, Category, Tag
from .serializers import BlogSerializer, CategorySerializer, TagSerializer
from rest_framework.filters import SearchFilter
from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import PermissionDenied

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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import BlogReactionSerializer

class BlogReactionAPIView(APIView):
    def get(self, request, pk):
        """
        Retrieve a blog and increment its views count.
        """
        try:
            blog = Blog.objects.get(pk=pk, is_published=True)
            blog.views_count += 1  # Increment the view count
            blog.save(update_fields=['views_count'])
            serializer = BlogReactionSerializer(blog)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Blog.DoesNotExist:
            return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk):
        """
        Allow users to react to a blog (Good or Bad).
        """
        try:
            blog = Blog.objects.get(pk=pk, is_published=True)
            reaction = request.data.get('reaction')  # 'good' or 'bad'

            if reaction == 'good':
                blog.good_reactions += 1
            elif reaction == 'bad':
                blog.bad_reactions += 1
            else:
                return Response({'error': 'Invalid reaction'}, status=status.HTTP_400_BAD_REQUEST)

            blog.save(update_fields=['good_reactions', 'bad_reactions'])
            serializer = BlogReactionSerializer(blog)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Blog.DoesNotExist:
            return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
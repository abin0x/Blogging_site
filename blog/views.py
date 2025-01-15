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
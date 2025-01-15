# urls.py
from django.urls import path
from .views import BlogListCreateAPIView, BlogDetailAPIView,CategoryListCreateAPIView, TagListCreateAPIView, BlogSearchAPIView

urlpatterns = [
    path('blogs/', BlogListCreateAPIView.as_view(), name='blog-list-create'),
    path('blogs/<int:pk>/', BlogDetailAPIView.as_view(), name='blog-detail'),
    path('categories/', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('tags/', TagListCreateAPIView.as_view(), name='tag-list-create'),
    path('search/', BlogSearchAPIView.as_view(), name='blog-search'),
]

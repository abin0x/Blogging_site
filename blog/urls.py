# urls.py
from django.urls import path
from .views import BlogListCreateAPIView, BlogDetailAPIView,CategoryListCreateAPIView, TagListCreateAPIView, BlogSearchAPIView, BlogReactionAPIView,BlogByCategoryAPIView

urlpatterns = [
    path('blogs/', BlogListCreateAPIView.as_view(), name='blog-list-create'),
    path('blogs/<int:pk>/', BlogDetailAPIView.as_view(), name='blog-detail'),
    path('categories/', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('tags/', TagListCreateAPIView.as_view(), name='tag-list-create'),
    path('search/', BlogSearchAPIView.as_view(), name='blog-search'),
    path('blogs/<int:pk>/react/', BlogReactionAPIView.as_view(), name='blog-react'),
    path('cat/<int:category_id>/blogs/', BlogByCategoryAPIView.as_view(), name='category-blogs'),
    # path('blogs/<int:blog_id>/comments/', CommentListCreateAPIView.as_view(), name='blog-comments'),

]

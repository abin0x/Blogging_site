# urls.py
from django.urls import path
from .views import BlogListCreateAPIView, BlogDetailAPIView,CategoryListCreateAPIView, TagListCreateAPIView, BlogSearchAPIView, BlogReactionAPIView,BlogByCategoryAPIView, BlogSubmissionListCreateAPIView,MediaItemListCreateView,MediaItemDetailView,MediaCardListCreateAPIView, PlaylistVideoListAPIView,DashboardAPIView

urlpatterns = [
    path('blogs/', BlogListCreateAPIView.as_view(), name='blog-list-create'),
    path('blogs/<int:pk>/', BlogDetailAPIView.as_view(), name='blog-detail'),
    path('categories/', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('tags/', TagListCreateAPIView.as_view(), name='tag-list-create'),
    path('search/', BlogSearchAPIView.as_view(), name='blog-search'),
    path('blogs/<int:pk>/react/', BlogReactionAPIView.as_view(), name='blog-react'),
    path('cat/<int:category_id>/blogs/', BlogByCategoryAPIView.as_view(), name='category-blogs'),
    path('blogs/<int:pk>/download-pdf/', BlogDetailAPIView.as_view(), name='blog-pdf-download'),
    path('submissions/', BlogSubmissionListCreateAPIView.as_view(), name='blog-submissions'),
    # path('media/', MediaItemViewSet.as_view({'post': 'create'}), name='media-item-create'),
    # path('media/', MediaItemListCreateView.as_view(), name='media-item-list'),
    # path('media/<int:pk>/',MediaItemDetailView.as_view(), name='media-item-detail'),
    path('media/', MediaCardListCreateAPIView.as_view(), name='media-card-create'),
    path('media/<str:playlist_id>/', PlaylistVideoListAPIView.as_view(), name='playlist-video-list'),
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),
]
    # path('blogs/<int:blog_id>/comments/', CommentListCreateAPIView.as_view(), name='blog-comments'),



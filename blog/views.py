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
from rest_framework.pagination import PageNumberPagination



class BlogReactionAPIView(generics.CreateAPIView):
    serializer_class = BlogReactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BlogPagination(PageNumberPagination):
    page_size = 5  # Set the number of blogs per page
    page_size_query_param = 'page_size'  # Allows clients to override page_size via query params
    max_page_size = 100  # Optional: set a maximum page size limit

# Blog Views
class BlogListCreateAPIView(generics.ListCreateAPIView):
    queryset = Blog.objects.filter(is_published=True).order_by('-created_at')
    # queryset = Blog.objects.filter(is_published=True)
    serializer_class = BlogSerializer
    pagination_class = BlogPagination
    # permission_classes = [IsAuthenticatedOrReadOnly]  

    def perform_create(self, serializer):
        # serializer.save(author=self.request.user)
        serializer.save()






from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


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
        
        # Fetch blogs in the same category, excluding the current blog
        related_blogs = Blog.objects.filter(category=blog.category).exclude(id=blog.id) #এটা নতুন লাইন আপডেট করা হয়েছে।

        # Include related blogs in the response
        response = self.retrieve(request, *args, **kwargs) #এটা নতুন লাইন আপডেট করা হয়েছে।
        response.data['related_blogs'] = BlogSerializer(related_blogs, many=True).data #এটা নতুন লাইন আপডেট করা হয়েছে।

        # return self.retrieve(request, *args, **kwargs)
        return response #এটা নতুন লাইন আপডেট করা হয়েছে।

    def get_client_ip(self, request):
        """Helper function to get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    def download_pdf(self, request, *args, **kwargs):
    
        blog = self.get_object()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{blog.title}.pdf"'

        # Create PDF
        pdf = canvas.Canvas(response, pagesize=letter)
        pdf.setFont("Helvetica", 12)

        # Write the blog content to the PDF
        pdf.drawString(100, 750, f"Blog Title: {blog.title}")
        pdf.drawString(100, 730, f"Author: {blog.author.username}")
        pdf.drawString(100, 710, f"Published: {blog.created_at.strftime('%Y-%m-%d')}")
        pdf.drawString(100, 690, f"Reading Time: {blog.reading_time} mins")
        pdf.drawString(100, 670, f"Category: {blog.category.name}")
        pdf.drawString(100, 650, f"Content:")
        text_object = pdf.beginText(100, 630)
        text_object.setFont("Helvetica", 10)
        text_object.textLines(blog.content)
        pdf.drawText(text_object)

        # Save the PDF
        pdf.showPage()
        pdf.save()

        return response




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


# class BlogByCategoryAPIView(generics.ListAPIView):
#     serializer_class = BlogSerializer
#     permission_classes = [IsAuthenticatedOrReadOnly]

#     def get_queryset(self):
#         category_id = self.kwargs['category_id']
#         return Blog.objects.filter(category__id=category_id, is_published=True)  # Filter by category

from rest_framework.pagination import PageNumberPagination

class BlogByCategoryPagination(PageNumberPagination):
    page_size = 6  # Number of blogs per page
    page_size_query_param = 'page_size'  # Allow the client to set the page size
    max_page_size = 10  # Maximum number of blogs per page

class BlogByCategoryAPIView(generics.ListAPIView):
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = BlogByCategoryPagination

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Blog.objects.filter(category__id=category_id, is_published=True)  # Filter by category


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


class BlogReactionAPIView(generics.UpdateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogReactionSerializer

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

        # If the reaction is the same as before, allow the user to change it
        if not created and user_reaction.reaction == reaction:
            return Response({'error': 'You have already reacted with this choice. You can change it.'}, status=status.HTTP_400_BAD_REQUEST)

        # Decrement the old reaction count (if the user had already reacted)
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
    





from rest_framework import generics, permissions
from .models import BlogSubmission
from .serializers import BlogSubmissionSerializer

class BlogSubmissionListCreateAPIView(generics.ListCreateAPIView):
    queryset = BlogSubmission.objects.all()
    serializer_class = BlogSubmissionSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MediaItem
from .serializers import MediaItemSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import MediaItem
from .serializers import MediaItemSerializer

class MediaItemListCreateView(generics.ListCreateAPIView):
    """
    API view to list all media items or create a new one.
    """
    queryset = MediaItem.objects.all()
    serializer_class = MediaItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Anyone can view, but only authenticated users can create

    def create(self, request, *args, **kwargs):
        """
        Custom create method to handle additional validation if needed.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MediaItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a media item.
    """
    queryset = MediaItem.objects.all()
    serializer_class = MediaItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Authenticated users can modify, others can only view

    def update(self, request, *args, **kwargs):
        """
        Custom update method to handle media updates.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
        Custom delete method with a success response.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Media item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
from googleapiclient.discovery import build
from django.conf import settings
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from .models import MediaCard
from .serializers import MediaCardSerializer


# Initialize the YouTube API client
def get_youtube_service():
    api_key = settings.YOUTUBE_API_KEY  # Retrieve the API key from settings
    return build('youtube', 'v3', developerKey=api_key)

# Fetch videos from a YouTube playlist
def get_playlist_videos(playlist_id):
    youtube = get_youtube_service()
    
    # Request to fetch playlist items
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=50  # Max number of results to fetch (you can adjust this)
    )
    response = request.execute()
    
    videos = []
    for item in response['items']:
        video_id = item['snippet']['resourceId']['videoId']
        title = item['snippet']['title']
        description = item['snippet']['description']
        thumbnail = item['snippet']['thumbnails']['high']['url']
        
        videos.append({
            'video_id': video_id,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
            'url': f'https://www.youtube.com/watch?v={video_id}'
        })
    
    return videos

# MediaCard List and Create API using generics
class MediaCardListCreateAPIView(generics.ListCreateAPIView):
    queryset = MediaCard.objects.all()
    serializer_class = MediaCardSerializer

    def perform_create(self, serializer):
        """
        Override the create method to handle additional logic when creating a MediaCard.
        """
        serializer.save()

# Playlist Video List API using APIView (since we interact with the YouTube API)
class PlaylistVideoListAPIView(APIView):
    """
    API view for listing videos in a specific YouTube playlist.
    """
    def get(self, request, playlist_id):
        # Get the videos from the YouTube playlist
        videos = get_playlist_videos(playlist_id)
        
        # Return the videos as JSON response
        return JsonResponse({'videos': videos})

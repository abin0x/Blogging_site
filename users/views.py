from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from rest_framework import status
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from .serializers import RegistrationSerializer, LoginSerializer, UserSerializer,UserDetailSerializer
from .models import CustomUser
from rest_framework.generics import RetrieveAPIView


class UserRegistrationAPIView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            # confirm_link = f"https://scl-nine.vercel.app/api/users/activate/{uid}/{token}/"
            confirm_link = f"http://127.0.0.1:8000/api/users/activate/{uid}/{token}/"

            email_subject = "Confirm Your Email"
            # email_template = 'confirm_author_email.html' if user.user_type == 'author' else 'confirm_modarator_email.html'
            email_template = 'confirm_author_email.html' if user.user_type == 'author' else 'confirm_modarator_email.html'

            email_body = render_to_string(email_template, {'confirm_link': confirm_link})

            email = EmailMultiAlternatives(email_subject, '', to=[user.email])
            email.attach_alternative(email_body, "text/html")
            email.send()

            return Response({"detail": "Check your email for confirmation"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def activate(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (CustomUser.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('http://127.0.0.1:8000/api/users/login/')
    return redirect('register')


class UserLoginApiView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutAPIView(APIView):
    def get(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass
        logout(request)
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


class UserListAPIView(APIView):
    def get(self, request):
        # Filter users based on user_type (you can customize this filter)
        users = CustomUser.objects.all()  # You can apply filters based on request.query_params
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailAPIView(RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = 'pk'


class UserProfileUpdateAPIView(APIView):
    def patch(self, request, pk):
        if request.user.pk != pk:
            return Response({"detail": "You cannot update another user's profile."}, status=status.HTTP_403_FORBIDDEN)

        user = request.user
        serializer = UserDetailSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
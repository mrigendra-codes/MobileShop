from django.shortcuts import render
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import MainUserSerializer, UserRegisterSerializer, UserLoginSerializer, RetailerProfileSerializer
from .models import MainUser, RetailerProfile, RetailerStore
# Create your views here.

class ProfileView(APIView):
    permission_classes = [AllowAny,]


    def get(self, request):
        users = MainUser.objects.all()
        serializer = MainUserSerializer(users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRegisterView(CreateAPIView):
    queryset = MainUser.objects.all()
    serializer_class = UserRegisterSerializer


class UserLoginView(APIView):
    permission_classes = [AllowAny,]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={"request":request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access" : str(refresh.access_token),
                "refresh" : str(refresh),
                "user" : {
                    "email":user.email,
                    "username":user.username,
                    "first_name":user.first_name,
                    "last_name":user.last_name,
                },
                "status":status.HTTP_200_OK
            }
        )



class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated,]


    def post(self, request):
        try:
            token = RefreshToken(request_data=["refresh"])
            token.blacklist()
        except (KeyError, TokenError):
            raise Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class RetailerProfileView(APIView):
    permission_classes = [AllowAny,]

    def get(self, request, pk):
        profile = get_object_or_404(RetailerProfile, user__username=pk)
        serializer = RetailerProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
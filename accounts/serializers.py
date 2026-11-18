from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

from .models import MainUser, RetailerProfile, RetailerStore


class MainUserSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    email = serializers.EmailField()
    username = serializers.CharField(max_length=100, required=True)
    first_name = serializers.CharField(max_length=True, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(max_length=100, allow_blank=True, allow_null=True)



class UserRegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, required=True, style=({"input_type": "password"}))
    password2 = serializers.CharField(write_only=True, required=True, style=({"input_type": "password"}))
    class Meta:
        model = MainUser
        fields = ["email", "first_name", "last_name", "username", "phone_number", "password1", "password2"]


    def validate(self, attrs):
        password1 = attrs.get("password1")
        password2 = attrs.get("password2")

        if password1 != password2:
            raise serializers.ValidationError({"error":"Password does not match."})

        validate_password(password1)
        return attrs

    def validate_email(self, value):
        if MainUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exist.")
        return value.lower()

    def create(self, validated_data):
        validated_data.pop("password1")
        password = validated_data.pop("password2")

        user = MainUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style=({'input_type':"password"}))
    class Meta:
        model = MainUser
        fields = ["email",  "password"]


    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password
        )

        if user is None:
            raise serializers.ValidationError("Invalid email or password")
        if not user.is_active:
            raise serializers.ValidationError("This user is disabled")

        attrs["user"] = user

        return attrs


class RetailerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetailerProfile
        fields = ["user", "shop_name", "whatsapp_number", "business_email", "shop_logo", "gst_number", "approval_status", "credit_enabled", "credit_limit", "created_at"]



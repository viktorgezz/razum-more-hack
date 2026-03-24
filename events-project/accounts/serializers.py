from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "city", "role", "is_verified", "points", "total_events")
        read_only_fields = fields

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True, label="Подтверждение пароля")

    class Meta:
        model = User
        fields = ("username", "password", "password2", "first_name", "last_name", "email", "city")
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name":  {"required": True},
            "email":      {"required": False},
            "city":       {"required": False},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data, role=User.Role.PARTICIPANT, is_verified=False)
        user.set_password(password)
        user.save()
        return user

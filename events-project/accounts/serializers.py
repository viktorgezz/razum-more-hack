from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "role",
            "city",
            "birth_date",
            "avatar",
        )
        read_only_fields = ("id",)

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=False)
    email = serializers.EmailField(required=False, allow_blank=False)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        password = attrs.get("password")

        if not username and not email:
            raise serializers.ValidationError("Укажите username или email.")
        if username and email:
            raise serializers.ValidationError("Используйте только один идентификатор: username или email.")

        if email:
            user = User.objects.filter(email__iexact=email).first()
            username = user.username if user else None

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Неверные учетные данные.")
        if not user.is_active:
            raise serializers.ValidationError("Пользователь деактивирован.")

        attrs["user"] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "city",
            "birth_date",
            "avatar",
            "is_verified",
            "date_joined",
        )

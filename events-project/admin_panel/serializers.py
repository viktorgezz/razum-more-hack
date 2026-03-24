from django.contrib.auth import get_user_model
from rest_framework import serializers

from rating.models import PointWeight

User = get_user_model()


class PendingOrganizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "is_active", "is_staff")


class OrganizerModerationSerializer(serializers.Serializer):
    detail = serializers.CharField()
    user_id = serializers.IntegerField()
    is_staff = serializers.BooleanField()
    is_active = serializers.BooleanField()


class PointWeightReadSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    updated_by_username = serializers.CharField(source="updated_by.username", read_only=True)

    class Meta:
        model = PointWeight
        fields = (
            "id",
            "event_type",
            "category",
            "category_name",
            "weight",
            "updated_by",
            "updated_by_username",
            "updated_at",
        )


class PointWeightPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointWeight
        fields = ("weight", "category")

    def validate_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError("Вес должен быть больше 0.")
        return value

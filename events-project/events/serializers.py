from rest_framework import serializers

from .models import Event, EventCategory, Participation, Prize


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ["id", "name", "slug", "description"]


class PrizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prize
        fields = ["id", "event", "name", "description", "prize_type", "quantity", "created_at"]
        read_only_fields = ["id", "created_at", "event"]


class ParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participation
        fields = [
            "id",
            "event",
            "user",
            "status",
            "checked_in_at",
            "confirmed_at",
            "points_awarded",
            "created_at",
        ]
        read_only_fields = fields


class EventWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "organizer",
            "category",
            "name",
            "description",
            "event_date",
            "event_type",
            "difficulty_coef",
            "base_points",
            "max_participants",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organizer", "created_at", "updated_at"]


class EventReadSerializer(serializers.ModelSerializer):
    category = EventCategorySerializer(read_only=True)
    prizes = PrizeSerializer(many=True, read_only=True)
    participants_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "organizer",
            "category",
            "name",
            "description",
            "event_date",
            "event_type",
            "difficulty_coef",
            "base_points",
            "max_participants",
            "status",
            "participants_count",
            "prizes",
            "created_at",
            "updated_at",
        ]


class EventRegisterResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participation
        fields = ["id", "event", "user", "status", "qr_token", "points_awarded", "created_at"]
        read_only_fields = fields


class EventCheckinSerializer(serializers.Serializer):
    qr_token = serializers.CharField()

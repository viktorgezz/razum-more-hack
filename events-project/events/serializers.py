from rest_framework import serializers

from events.models import Event, EventCategory, Participation, Prize


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ("id", "name", "slug", "description")


class PrizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prize
        fields = ("id", "event", "name", "description", "prize_type", "quantity")
        read_only_fields = ("event",)


class EventSerializer(serializers.ModelSerializer):
    organizer_id = serializers.PrimaryKeyRelatedField(source="organizer", read_only=True)
    category = EventCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=EventCategory.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    prizes = PrizeSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "organizer_id",
            "category",
            "category_id",
            "name",
            "description",
            "event_date",
            "event_type",
            "difficulty_coef",
            "base_points",
            "max_participants",
            "status",
            "created_at",
            "prizes",
        )
        read_only_fields = ("id", "created_at")


class ParticipationSerializer(serializers.ModelSerializer):
    event_id = serializers.PrimaryKeyRelatedField(source="event", read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(source="user", read_only=True)

    class Meta:
        model = Participation
        fields = (
            "id",
            "event_id",
            "user_id",
            "status",
            "qr_token",
            "checked_in_at",
            "confirmed_at",
            "points_awarded",
            "created_at",
        )
        read_only_fields = fields

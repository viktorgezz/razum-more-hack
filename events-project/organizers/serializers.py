from rest_framework import serializers

from events.models import Event
from organizers.models import OrganizerReview


class OrganizerReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.SerializerMethodField()
    event_name = serializers.CharField(source='event.name', read_only=True)

    class Meta:
        model = OrganizerReview
        fields = [
            'id',
            'organizer',
            'reviewer',
            'reviewer_name',
            'event',
            'event_name',
            'score',
            'comment',
            'created_at',
        ]

    def get_reviewer_name(self, obj) -> str:
        return obj.reviewer.get_full_name() or obj.reviewer.username


class OrganizerReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizerReview
        fields = ['event', 'score', 'comment']


class OrganizerEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id',
            'name',
            'event_date',
            'event_type',
            'category',
            'difficulty_coef',
            'base_points',
            'status',
        ]


class OrganizerListSerializer(serializers.ModelSerializer):
    events_count = serializers.IntegerField(read_only=True)

    class Meta:
        from accounts.models import User
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'city',
            'is_verified',
            'events_count',
        ]


class OrganizerProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    avatar = serializers.ImageField(allow_null=True, required=False)
    city = serializers.CharField()
    is_verified = serializers.BooleanField()
    events_count = serializers.IntegerField()
    avg_trust_score = serializers.DecimalField(max_digits=3, decimal_places=2, allow_null=True)
    reviews_count = serializers.IntegerField()
    frequent_prizes = serializers.ListField(child=serializers.DictField())

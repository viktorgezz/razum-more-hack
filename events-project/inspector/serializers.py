from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class CandidateListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    date_joined = serializers.DateTimeField()
    events_count = serializers.IntegerField()
    confirmed_count = serializers.IntegerField()
    total_points = serializers.IntegerField()
    avg_points = serializers.FloatField()


class CandidateReportMetaSerializer(serializers.Serializer):
    candidate_id = serializers.IntegerField()
    generated_at = serializers.DateTimeField()

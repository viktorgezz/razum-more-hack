from rest_framework import serializers

from .models import PointWeight, RatingSnapshot


class PointWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointWeight
        fields = [
            'id',
            'event_type',
            'category',
            'weight',
            'updated_by',
            'updated_at',
        ]
        read_only_fields = ['updated_by', 'updated_at']


class RatingSnapshotSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = RatingSnapshot
        fields = [
            'id',
            'user',
            'username',
            'first_name',
            'last_name',
            'rating_it',
            'rating_social',
            'rating_media',
            'common_rating',
            'rank',
            'snapshot_date',
        ]

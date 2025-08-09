# monitor_app/serializers.py
from rest_framework import serializers
from .models import CongestionLevel,Collected

class CongestionLevelItemSerializer(serializers.ModelSerializer):
    # Locationの項目を直で出したいので source= で外部キー先を参照
    program_name = serializers.CharField(source='location.program_name', read_only=True)
    room_name    = serializers.CharField(source='location.room_name', read_only=True)
    comment      = serializers.CharField(source='location.comment', read_only=True)
    floor        = serializers.IntegerField(source='location.floor', read_only=True)

    class Meta:
        model  = CongestionLevel
        fields = ['program_name', 'room_name', 'level', 'reliability', 'comment', 'floor']

class CongestionLevelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collected
        fields = ['location', 'congestion_level']
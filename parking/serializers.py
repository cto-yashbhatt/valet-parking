# parking/serializers.py
from rest_framework import serializers
from .models import ParkingSlot

class ParkingSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSlot
        fields = [
            'id',
            'company',
            'name',
            'division',
            'qr_code_image',
            'is_active',
            'is_occupied',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

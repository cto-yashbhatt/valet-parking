# parking/serializers.py
from rest_framework import serializers
from .models import ParkingSlot, ParkingTransaction, Customer

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

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['phone_number', 'name']

class ParkingTransactionSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    slot = ParkingSlotSerializer(read_only=True)

    class Meta:
        model = ParkingTransaction
        fields = [
            'id',
            'customer',
            'slot',
            'employee_assigned',
            'plate_number',
            'status',
            'requested_at',
            'parked_at',
            'retrieve_requested_at',
            'delivered_at',
            'ticket_code',
        ]
        read_only_fields = ['id', 'requested_at']

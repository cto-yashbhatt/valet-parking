from django.db import models

# Create your models here.
# parking/models.py
import uuid
from django.db import models
from django.conf import settings

class ParkingSlot(models.Model):
    """
    Represents a slot that can be assigned to a car.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='parking_slots'
    )
    name = models.CharField(max_length=100)
    division = models.CharField(max_length=100)
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_occupied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'name')    # slot names unique per company

    def __str__(self):
        return f"{self.name} - {self.company.name}"

class Customer(models.Model):
    """
    Stores unique customers, keyed by phone_number.
    """
    id = models.BigAutoField(primary_key=True)
    phone_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.phone_number

class ParkingTransaction(models.Model):
    """
    Tracks each parking request: pending_park → parked → pending_retrieve → delivered.
    """
    class Status(models.TextChoices):
        PENDING_PARK = 'pending_park', 'Pending Park'
        PARKED = 'parked', 'Parked'
        PENDING_RETRIEVE = 'pending_retrieve', 'Pending Retrieve'
        DELIVERED = 'delivered', 'Delivered'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    slot = models.ForeignKey(
        ParkingSlot,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    employee_assigned = models.ForeignKey(
        'companies.EmployeeProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_transactions'
    )
    plate_number = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_PARK
    )
    requested_at = models.DateTimeField(auto_now_add=True)                # when customer first messages
    parked_at = models.DateTimeField(blank=True, null=True)               # when employee confirms “Parked”
    retrieve_requested_at = models.DateTimeField(blank=True, null=True)   # when customer says “Get my car”
    delivered_at = models.DateTimeField(blank=True, null=True)            # when employee marks “Delivered”
    raw_whatsapp_payload = models.JSONField(blank=True, null=True)        # store full webhook payload
    ticket_code = models.CharField(max_length=50, blank=True, null=True)  # optionally generated OTP/code

    def __str__(self):
        return f"TX {self.id} | Slot {self.slot.name} | Status {self.status}"

class NotificationLog(models.Model):
    """
    Logs each incoming/outgoing WhatsApp message.
    """
    class Direction(models.TextChoices):
        INCOMING = 'incoming', 'Incoming'
        OUTGOING = 'outgoing', 'Outgoing'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(
        ParkingTransaction,
        on_delete=models.CASCADE,
        related_name='notification_logs'
    )
    direction = models.CharField(max_length=10, choices=Direction.choices)
    whatsapp_message_id = models.CharField(max_length=100, blank=True, null=True)
    payload = models.JSONField()   # full WhatsApp payload or our custom structure
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log {self.id} | {self.direction} | TX {self.transaction.id}"

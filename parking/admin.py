from django.contrib import admin
from .models import ParkingSlot, Customer, ParkingTransaction, NotificationLog

# Register your models here.
# parking/admin.py

@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'is_active', 'is_occupied')
    list_filter = ('company', 'is_active', 'is_occupied')
    search_fields = ('name', 'company__name')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'name')
    search_fields = ('phone_number', 'name')

@admin.register(ParkingTransaction)
class ParkingTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'slot', 'customer', 'employee_assigned', 'status', 'requested_at')
    list_filter = ('status', 'slot__company')
    search_fields = ('id', 'customer__phone_number', 'slot__name')

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction', 'direction', 'timestamp')
    list_filter = ('direction',)
    search_fields = ('transaction__id', 'whatsapp_message_id')

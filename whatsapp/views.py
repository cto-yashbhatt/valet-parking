from django.shortcuts import render

# Create your views here.
# whatsapp/views.py
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from companies.models import EmployeeProfile, Company
from parking.models import Customer, ParkingSlot, ParkingTransaction, NotificationLog
from django.conf import settings

# If using Twilio’s helper library:
from twilio.rest import Client as TwilioClient


class WhatsAppWebhookAPIView(APIView):
    """Handles incoming messages from WhatsApp (via Twilio or WhatsApp Cloud API)."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Expected payload (example, Twilio):
        {
          "From": "whatsapp:+1234567890",
          "Body": "Park my car - GJ01AB1234 - <slot_uuid>",
          "MessageSid": "SMxxxxxxxxxxxx",
          ...
        }
        """
        payload = request.data.copy()
        # 1. Verify signature/header if required by your provider.
        #    If invalid, return HTTP 403.

        # 2. Parse sender phone & message:
        raw_from = payload.get('From', '')
        # Twilio’s format is "whatsapp:+1234567890", so strip “whatsapp:”
        phone = raw_from.replace("whatsapp:", "")
        body = payload.get('Body', '').strip()

        # 3. Log incoming message
        #    If we cannot parse a valid slot_id, respond with an error message
        #    and log that in NotificationLog with direction='incoming'.
        try:
            # Basic parse: assume “Park my car – <plate> – <slot_uuid>”
            parts = [p.strip() for p in body.split('-')]
            if len(parts) < 2:
                raise ValueError("Invalid format.")

            command = parts[0].lower()  # e.g. "park my car"
            plate_number = parts[1]     # e.g. "GJ01AB1234"
            slot_uuid = parts[2]        # e.g. "550e8400-e29b-41d4-a716-446655440000"

            # Fetch or create Customer
            customer, _ = Customer.objects.get_or_create(phone_number=phone)

            # Fetch slot
            try:
                slot = ParkingSlot.objects.get(id=slot_uuid)
            except ParkingSlot.DoesNotExist:
                # Send error back to user
                self.send_whatsapp_message(phone, "Invalid slot. Please scan a valid QR code.")
                return Response(status=status.HTTP_200_OK)

            if slot.is_occupied:
                self.send_whatsapp_message(phone, "Sorry, that slot is currently occupied. Please try another slot.")
                return Response(status=status.HTTP_200_OK)

            # Create new transaction
            tx = ParkingTransaction.objects.create(
                customer=customer,
                slot=slot,
                plate_number=plate_number,
                status=ParkingTransaction.Status.PENDING_PARK,
                raw_whatsapp_payload=payload
            )

            # Log incoming
            NotificationLog.objects.create(
                transaction=tx,
                direction=NotificationLog.Direction.INCOMING,
                whatsapp_message_id=payload.get('MessageSid', None),
                payload=payload
            )

            # Acknowledge to customer
            ack_text = f"Received your request to park car {plate_number} in slot {slot.name}. Please wait for confirmation."
            self.send_whatsapp_message(phone, ack_text)

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            # Log exception, but still respond 200 so provider won’t retry aggressively
            print(f"[Error parsing incoming WhatsApp] {e}")
            return Response(status=status.HTTP_200_OK)

    def send_whatsapp_message(self, to_phone, message_text):
        """
        Uses Twilio (or the WhatsApp Cloud API) to send an outbound message.
        Ensure you’ve set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_WHATSAPP_NUMBER in settings.
        """
        try:
            client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            msg = client.messages.create(
                from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
                body=message_text,
                to=f"whatsapp:{to_phone}"
            )
            # Optionally, log outbound message
            return msg.sid
        except Exception as ex:
            print(f"[Error sending WhatsApp] {ex}")
            return None


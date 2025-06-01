from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import ParkingSlot, ParkingTransaction
from .serializers import ParkingSlotSerializer, ParkingTransactionSerializer
# Create your views here.
# parking/views.py


class ParkingSlotListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/parking/slots/     → list all slots (optionally filter by company, etc.)
    POST /api/parking/slots/     → create a new ParkingSlot
    """
    queryset = ParkingSlot.objects.all()
    serializer_class = ParkingSlotSerializer
    permission_classes = [permissions.IsAuthenticated]  # adjust as needed

    def perform_create(self, serializer):
        # If you want to automatically assign the requesting user's company,
        # you could do something like:
        # serializer.save(company=self.request.user.employee_profile.company)
        # For now, let the client provide "company" in the POST data
        serializer.save()


class ParkingSlotRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/parking/slots/<uuid:pk>/     → retrieve one slot
    PUT    /api/parking/slots/<uuid:pk>/     → update
    PATCH  /api/parking/slots/<uuid:pk>/     → partial update
    DELETE /api/parking/slots/<uuid:pk>/     → delete
    """
    queryset = ParkingSlot.objects.all()
    serializer_class = ParkingSlotSerializer
    permission_classes = [permissions.IsAuthenticated]


class ParkingTransactionListAPIView(generics.ListAPIView):
    """
    GET /api/parking/transactions/ → list all transactions
    """
    queryset = ParkingTransaction.objects.all().select_related('customer', 'slot', 'employee_assigned')
    serializer_class = ParkingTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Add filtering by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by('-requested_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_transaction_status(request, transaction_id):
    """
    POST /api/parking/transactions/<uuid:transaction_id>/update-status/
    Body: {"status": "parked|pending_retrieve|delivered"}
    """
    try:
        transaction = ParkingTransaction.objects.get(id=transaction_id)
    except ParkingTransaction.DoesNotExist:
        return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if new_status not in [choice[0] for choice in ParkingTransaction.Status.choices]:
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

    # Update status and timestamps
    transaction.status = new_status
    if new_status == ParkingTransaction.Status.PARKED:
        transaction.parked_at = timezone.now()
        # Mark slot as occupied
        transaction.slot.is_occupied = True
        transaction.slot.save()
    elif new_status == ParkingTransaction.Status.PENDING_RETRIEVE:
        transaction.retrieve_requested_at = timezone.now()
    elif new_status == ParkingTransaction.Status.DELIVERED:
        transaction.delivered_at = timezone.now()
        # Mark slot as available
        transaction.slot.is_occupied = False
        transaction.slot.save()

    transaction.save()

    serializer = ParkingTransactionSerializer(transaction)
    return Response(serializer.data)

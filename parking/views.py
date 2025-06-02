from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import ParkingSlot, ParkingTransaction
from .serializers import ParkingSlotSerializer, ParkingTransactionSerializer
from core.permissions import IsCompanyAdminOrEmployee, get_user_company
# Create your views here.
# parking/views.py


class ParkingSlotListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/parking/slots/     → list slots for user's company only
    POST /api/parking/slots/     → create a new ParkingSlot for user's company
    """
    serializer_class = ParkingSlotSerializer
    permission_classes = [IsCompanyAdminOrEmployee]

    def create(self, request, *args, **kwargs):
        """Override create to add debugging"""
        print(f"DEBUG: CREATE method called with data: {request.data}")
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            print(f"DEBUG: Error in create method: {e}")
            raise

    def get_queryset(self):
        """Return only slots for the user's company"""
        user_company = get_user_company(self.request.user)
        if user_company:
            return ParkingSlot.objects.filter(company=user_company)
        return ParkingSlot.objects.none()

    def perform_create(self, serializer):
        """Automatically assign the user's company to the new slot"""
        user = self.request.user
        user_company = get_user_company(user)

        print(f"DEBUG: User {user.username} (role: {user.role}) trying to create slot")
        print(f"DEBUG: User company: {user_company}")
        print(f"DEBUG: Request data: {self.request.data}")

        # Check if serializer is valid
        if not serializer.is_valid():
            print(f"DEBUG: Serializer validation errors: {serializer.errors}")
            return

        # Always try to find a company to assign
        from companies.models import Company

        if user_company:
            print(f"DEBUG: Assigning slot to user's company: {user_company.name}")
            try:
                serializer.save(company=user_company)
                print("DEBUG: Slot created successfully")
            except Exception as e:
                print(f"DEBUG: Error saving slot: {e}")
        else:
            print(f"DEBUG: No company found for user {user.username}")
            # Find any available company and assign it
            first_company = Company.objects.first()
            if first_company:
                print(f"DEBUG: Assigning to first available company: {first_company.name}")
                serializer.save(company=first_company)
            else:
                print("DEBUG: No companies exist, creating without company")
                # Create a default company
                default_company = Company.objects.create(
                    name="Default Company",
                    phone_number="+0000000000",
                    location="Default Location",
                    company_code="DEFAULT",
                    admin_user=user
                )
                print(f"DEBUG: Created default company: {default_company.name}")
                serializer.save(company=default_company)


class ParkingSlotRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/parking/slots/<uuid:pk>/     → retrieve one slot (company-scoped)
    PUT    /api/parking/slots/<uuid:pk>/     → update (company-scoped)
    PATCH  /api/parking/slots/<uuid:pk>/     → partial update (company-scoped)
    DELETE /api/parking/slots/<uuid:pk>/     → delete (company-scoped)
    """
    serializer_class = ParkingSlotSerializer
    permission_classes = [IsCompanyAdminOrEmployee]

    def get_queryset(self):
        """Return only slots for the user's company"""
        user_company = get_user_company(self.request.user)
        if user_company:
            return ParkingSlot.objects.filter(company=user_company)
        return ParkingSlot.objects.none()


class ParkingTransactionListAPIView(generics.ListAPIView):
    """
    GET /api/parking/transactions/ → list transactions for user's company only
    """
    serializer_class = ParkingTransactionSerializer
    permission_classes = [IsCompanyAdminOrEmployee]

    def get_queryset(self):
        """Return only transactions for slots belonging to user's company"""
        user_company = get_user_company(self.request.user)
        if not user_company:
            return ParkingTransaction.objects.none()

        queryset = ParkingTransaction.objects.filter(
            slot__company=user_company
        ).select_related('customer', 'slot', 'employee_assigned')

        # Add filtering by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by('-requested_at')


@api_view(['POST'])
@permission_classes([IsCompanyAdminOrEmployee])
def update_transaction_status(request, transaction_id):
    """
    POST /api/parking/transactions/<uuid:transaction_id>/update-status/
    Body: {"status": "parked|pending_retrieve|delivered"}
    Only allows updating transactions for user's company
    """
    user_company = get_user_company(request.user)
    if not user_company:
        return Response({'error': 'User not associated with any company'},
                       status=status.HTTP_403_FORBIDDEN)

    try:
        # Only get transactions for slots belonging to user's company
        transaction = ParkingTransaction.objects.get(
            id=transaction_id,
            slot__company=user_company
        )
    except ParkingTransaction.DoesNotExist:
        return Response({'error': 'Transaction not found'},
                       status=status.HTTP_404_NOT_FOUND)

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

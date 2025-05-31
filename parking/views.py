from django.shortcuts import render
from rest_framework import generics, permissions
from .models import ParkingSlot
from .serializers import ParkingSlotSerializer
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

# parking/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # List all slots or create a new one
    path('slots/', views.ParkingSlotListCreateAPIView.as_view(), name='slot-list-create'),

    # Retrieve, update, or delete a single slot by UUID
    path('slots/<uuid:pk>/', views.ParkingSlotRetrieveUpdateDestroyAPIView.as_view(), name='slot-detail'),

    # Transaction endpoints
    path('transactions/', views.ParkingTransactionListAPIView.as_view(), name='transaction-list'),
    path('transactions/<uuid:transaction_id>/update-status/', views.update_transaction_status, name='transaction-update-status'),
]

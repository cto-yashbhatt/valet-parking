# parking/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # List all slots or create a new one
    path('slots/', views.ParkingSlotListCreateAPIView.as_view(), name='slot-list-create'),

    # Retrieve, update, or delete a single slot by UUID
    path('slots/<uuid:pk>/', views.ParkingSlotRetrieveUpdateDestroyAPIView.as_view(), name='slot-detail'),

    # (Later, when you implement transaction-specific views, add them here:)
    # path('transactions/pending/', views.PendingParkTransactionListAPIView.as_view(), …),
    # path('transactions/<uuid:pk>/park/', views.ConfirmParkAPIView.as_view(), …),
    # etc.
]

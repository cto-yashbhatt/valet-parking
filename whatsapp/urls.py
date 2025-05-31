# whatsapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Example: the webhook endpoint
    path('webhook/', views.WhatsAppWebhookAPIView.as_view(), name='whatsapp-webhook'),
]


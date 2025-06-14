"""
URL configuration for valet_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# valet_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Frontend UI
    path('', include('frontend.urls')),

    # Authentication endpoints
    path('api/auth/', include('authentication.urls')),

    # Accounts (registration, login, logout) can be handled here or via DRF’s token endpoints.
    path('api-auth/', include('rest_framework.urls')),

    # Companies management (CRUD for companies & employees)
    path('api/companies/', include('companies.urls')),

    # Parking slot & transaction endpoints
    path('api/parking/', include('parking.urls')),

    # WhatsApp webhook endpoint
    path('api/whatsapp/', include('whatsapp.urls')),
    # 1. Schema (raw OpenAPI JSON):
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # 2. Swagger UI:
    path(
        'api/docs/swagger/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
